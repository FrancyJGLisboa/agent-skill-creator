#!/usr/bin/env python3
"""Fetch and format a live, read-only Open-Meteo weather briefing."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 20
MAX_ATTEMPTS = 3
WEATHER_CODES = {0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers", 81: "Rain showers", 82: "Violent rain showers", 95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with hail"}


def fetch_json(base_url: str, params: dict[str, str | int | float]) -> tuple[dict, str]:
    """Fetch one JSON response over HTTPS and return it with its exact URL."""
    url = f"{base_url}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "live-weather-briefing-skill/1.0"})
    for attempt in range(MAX_ATTEMPTS):
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 -- fixed HTTPS hosts
                return json.load(response), url
        except (HTTPError, URLError, TimeoutError) as exc:
            if attempt == MAX_ATTEMPTS - 1:
                raise exc
            time.sleep(attempt + 1)
    raise RuntimeError("unreachable retry state")


def geocoding_params(city: str) -> dict[str, str | int]:
    """Map ``City, CC`` input to Open-Meteo's name and countryCode parameters."""
    parts = [part.strip() for part in city.rsplit(",", 1)]
    params: dict[str, str | int] = {"name": city, "count": 1, "language": "en", "format": "json"}
    if len(parts) == 2 and len(parts[1]) == 2 and parts[1].isalpha():
        params["name"] = parts[0]
        params["countryCode"] = parts[1].upper()
    return params


def build_briefing(city: str) -> str:
    """Resolve ``city`` and return a Markdown briefing based on live API data."""
    geocoding, geocoding_url = fetch_json(GEOCODING_URL, geocoding_params(city))
    results = geocoding.get("results") or []
    if not results:
        raise ValueError(f"No location found for {city!r}; add a country or region.")
    location = results[0]
    forecast, forecast_url = fetch_json(FORECAST_URL, {"latitude": location["latitude"], "longitude": location["longitude"], "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m", "timezone": "auto"})
    current = forecast.get("current")
    if not isinstance(current, dict):
        raise ValueError("Forecast response did not contain current conditions.")
    required = ("time", "temperature_2m", "apparent_temperature", "weather_code", "wind_speed_10m")
    if any(key not in current for key in required):
        raise ValueError("Forecast response is missing one or more required current fields.")
    code = int(current["weather_code"])
    label = WEATHER_CODES.get(code, f"Weather code {code}")
    place = ", ".join(filter(None, [location.get("name"), location.get("admin1"), location.get("country")]))
    return "\n".join([
        f"# Current weather: {place}", "", f"Observed: {current['time']} ({forecast.get('timezone', 'local time')})", "",
        f"- Condition: {label}", f"- Temperature: {current['temperature_2m']} °C", f"- Feels like: {current['apparent_temperature']} °C", f"- Wind: {current['wind_speed_10m']} km/h", f"- Coordinates: {location['latitude']}, {location['longitude']}", "",
        "Advisory only: check official local warnings before safety-critical decisions.", "", "## Live sources", f"- Geocoding: {geocoding_url}", f"- Forecast: {forecast_url}", "",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a live Open-Meteo weather briefing.")
    parser.add_argument("--city", help="City name, preferably with country or region.")
    parser.add_argument("--input", help="Optional text file containing the city name; used by evals.")
    parser.add_argument("--output", required=True, help="Markdown briefing path.")
    args = parser.parse_args(argv)
    try:
        city = Path(args.input).read_text(encoding="utf-8").strip() if args.input else (args.city or "")
        if not city:
            raise ValueError("City name is empty.")
        Path(args.output).write_text(build_briefing(city), encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError, HTTPError, URLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
