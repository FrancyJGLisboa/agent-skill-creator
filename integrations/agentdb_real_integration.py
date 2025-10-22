#!/usr/bin/env python3
"""
Real AgentDB Integration - TypeScript/Python Bridge

This module provides real integration with AgentDB CLI, handling the TypeScript/Python
communication barrier while maintaining the "invisible intelligence" experience.

Architecture: Python <-> CLI Bridge <-> AgentDB (TypeScript/Node.js)
"""

import json
import subprocess
import logging
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import time

logger = logging.getLogger(__name__)

@dataclass
class Episode:
    """Python representation of AgentDB Episode"""
    session_id: str
    task: str
    input: Optional[str] = None
    output: Optional[str] = None
    critique: Optional[str] = None
    reward: float = 0.0
    success: bool = False
    latency_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Skill:
    """Python representation of AgentDB Skill"""
    name: str
    description: Optional[str] = None
    code: Optional[str] = None
    signature: Optional[Dict[str, Any]] = None
    success_rate: float = 0.0
    uses: int = 0
    avg_reward: float = 0.0
    avg_latency_ms: int = 0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CausalEdge:
    """Python representation of AgentDB CausalEdge"""
    cause: str
    effect: str
    uplift: float
    confidence: float = 0.5
    sample_size: Optional[int] = None
    mechanism: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentDBCLIException(Exception):
    """Custom exception for AgentDB CLI errors"""
    pass

class RealAgentDBBridge:
    """
    Real bridge to AgentDB CLI, providing Python interface while maintaining
    the "invisible intelligence" experience for users.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the real AgentDB bridge.

        Args:
            db_path: Path to AgentDB database file (default: ./agentdb.db)
        """
        self.db_path = db_path or "./agentdb.db"
        self.is_available = self._check_agentdb_availability()
        self._setup_environment()

    def _check_agentdb_availability(self) -> bool:
        """Check if AgentDB CLI is available"""
        try:
            result = subprocess.run(
                ["agentdb", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("AgentDB CLI not available")
            return False

    def _setup_environment(self):
        """Setup environment variables for AgentDB"""
        env = os.environ.copy()
        env["AGENTDB_PATH"] = self.db_path
        self.env = env

    def _run_agentdb_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """
        Execute AgentDB CLI command and parse output.

        Args:
            command: Command components
            timeout: Command timeout in seconds

        Returns:
            Parsed result dictionary

        Raises:
            AgentDBCLIException: If command fails
        """
        if not self.is_available:
            raise AgentDBCLIException("AgentDB CLI not available")

        try:
            full_command = ["agentdb"] + command
            logger.debug(f"Running AgentDB command: {' '.join(full_command)}")

            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self.env
            )

            if result.returncode != 0:
                error_msg = f"AgentDB command failed: {result.stderr}"
                logger.error(error_msg)
                raise AgentDBCLIException(error_msg)

            # Parse output (most AgentDB commands return structured text)
            return self._parse_agentdb_output(result.stdout)

        except subprocess.TimeoutExpired:
            raise AgentDBCLIException(f"AgentDB command timed out: {' '.join(command)}")
        except Exception as e:
            raise AgentDBCLIException(f"Error executing AgentDB command: {str(e)}")

    def _parse_agentdb_output(self, output: str) -> Dict[str, Any]:
        """
        Parse AgentDB CLI output into structured data.
        This is a simplified parser - real implementation would need
        to handle different output formats from different commands.
        """
        lines = output.strip().split('\n')

        # Look for JSON patterns or structured data
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue

        # Fallback: extract key information using patterns
        result = {
            "raw_output": output,
            "success": True,
            "data": {}
        }

        # Extract common patterns - handle ANSI escape codes
        if "Stored episode #" in output:
            # Extract episode ID
            for line in lines:
                if "Stored episode #" in line:
                    parts = line.split('#')
                    if len(parts) > 1:
                        # Remove ANSI escape codes and extract ID
                        id_part = parts[1].split()[0].replace('\x1b[0m', '')
                        try:
                            result["data"]["episode_id"] = int(id_part)
                        except ValueError:
                            result["data"]["episode_id"] = id_part
                        break

        elif "Created skill #" in output:
            # Extract skill ID
            for line in lines:
                if "Created skill #" in line:
                    parts = line.split('#')
                    if len(parts) > 1:
                        # Remove ANSI escape codes and extract ID
                        id_part = parts[1].split()[0].replace('\x1b[0m', '')
                        try:
                            result["data"]["skill_id"] = int(id_part)
                        except ValueError:
                            result["data"]["skill_id"] = id_part
                        break

        elif "Added causal edge #" in output:
            # Extract edge ID
            for line in lines:
                if "Added causal edge #" in line:
                    parts = line.split('#')
                    if len(parts) > 1:
                        # Remove ANSI escape codes and extract ID
                        id_part = parts[1].split()[0].replace('\x1b[0m', '')
                        try:
                            result["data"]["edge_id"] = int(id_part)
                        except ValueError:
                            result["data"]["edge_id"] = id_part
                        break

        elif "Retrieved" in output and "relevant episodes" in output:
            # Parse episode retrieval results
            result["data"]["episodes"] = self._parse_episodes_output(output)

        elif "Found" in output and "matching skills" in output:
            # Parse skill search results
            result["data"]["skills"] = self._parse_skills_output(output)

        return result

    def _parse_episodes_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse episodes from AgentDB output"""
        episodes = []
        lines = output.split('\n')
        current_episode = {}

        for line in lines:
            line = line.strip()
            if line.startswith("#") and "Episode" in line:
                if current_episode:
                    episodes.append(current_episode)
                current_episode = {"episode_id": line.split()[1].replace(":", "")}
            elif ":" in line and current_episode:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "Task":
                    current_episode["task"] = value
                elif key == "Reward":
                    try:
                        current_episode["reward"] = float(value)
                    except ValueError:
                        pass
                elif key == "Success":
                    current_episode["success"] = "Yes" in value
                elif key == "Similarity":
                    try:
                        current_episode["similarity"] = float(value)
                    except ValueError:
                        pass
                elif key == "Critique":
                    current_episode["critique"] = value

        if current_episode:
            episodes.append(current_episode)

        return episodes

    def _parse_skills_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse skills from AgentDB output"""
        skills = []
        lines = output.split('\n')
        current_skill = {}

        for line in lines:
            line = line.strip()
            if line.startswith("#") and not line.startswith("═"):
                if current_skill:
                    skills.append(current_skill)
                skill_name = line.replace("#1:", "").strip()
                current_skill = {"name": skill_name}
            elif ":" in line and current_skill:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "Description":
                    current_skill["description"] = value
                elif key == "Success Rate":
                    try:
                        current_skill["success_rate"] = float(value.replace("%", "")) / 100
                    except ValueError:
                        pass
                elif key == "Uses":
                    try:
                        current_skill["uses"] = int(value)
                    except ValueError:
                        pass
                elif key == "Avg Reward":
                    try:
                        current_skill["avg_reward"] = float(value)
                    except ValueError:
                        pass

        if current_skill:
            skills.append(current_skill)

        return skills

    # Reflexion Memory Methods

    def store_episode(self, episode: Episode) -> Optional[int]:
        """
        Store a reflexion episode in AgentDB.

        Args:
            episode: Episode to store

        Returns:
            Episode ID if successful, None otherwise
        """
        try:
            command = [
                "reflexion", "store",
                episode.session_id,
                episode.task,
                str(episode.reward),
                "true" if episode.success else "false"
            ]

            if episode.critique:
                command.append(episode.critique)
            if episode.input:
                command.append(episode.input)
            if episode.output:
                command.append(episode.output)
            if episode.latency_ms:
                command.append(str(episode.latency_ms))
            if episode.tokens_used:
                command.append(str(episode.tokens_used))

            result = self._run_agentdb_command(command)
            return result.get("data", {}).get("episode_id")

        except AgentDBCLIException as e:
            logger.error(f"Failed to store episode: {e}")
            return None

    def retrieve_episodes(self, task: str, k: int = 5, min_reward: float = 0.0,
                         only_failures: bool = False, only_successes: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve relevant episodes from AgentDB.

        Args:
            task: Task description
            k: Maximum number of episodes to retrieve
            min_reward: Minimum reward threshold
            only_failures: Only retrieve failed episodes
            only_successes: Only retrieve successful episodes

        Returns:
            List of episodes
        """
        try:
            command = ["reflexion", "retrieve", task, str(k), str(min_reward)]

            if only_failures:
                command.append("true")
            elif only_successes:
                command.append("false")

            result = self._run_agentdb_command(command)
            return result.get("data", {}).get("episodes", [])

        except AgentDBCLIException as e:
            logger.error(f"Failed to retrieve episodes: {e}")
            return []

    def get_critique_summary(self, task: str, only_failures: bool = False) -> Optional[str]:
        """Get critique summary for a task"""
        try:
            command = ["reflexion", "critique-summary", task]
            if only_failures:
                command.append("true")

            result = self._run_agentdb_command(command)
            # The summary is usually in the raw output
            return result.get("raw_output", "").split("═")[-1].strip()

        except AgentDBCLIException as e:
            logger.error(f"Failed to get critique summary: {e}")
            return None

    # Skill Library Methods

    def create_skill(self, skill: Skill) -> Optional[int]:
        """
        Create a skill in AgentDB.

        Args:
            skill: Skill to create

        Returns:
            Skill ID if successful, None otherwise
        """
        try:
            command = ["skill", "create", skill.name]

            if skill.description:
                command.append(skill.description)
            if skill.code:
                command.append(skill.code)

            result = self._run_agentdb_command(command)
            return result.get("data", {}).get("skill_id")

        except AgentDBCLIException as e:
            logger.error(f"Failed to create skill: {e}")
            return None

    def search_skills(self, query: str, k: int = 5, min_success_rate: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for skills in AgentDB.

        Args:
            query: Search query
            k: Maximum number of skills to retrieve
            min_success_rate: Minimum success rate threshold

        Returns:
            List of skills
        """
        try:
            command = ["skill", "search", query, str(k)]

            result = self._run_agentdb_command(command)
            return result.get("data", {}).get("skills", [])

        except AgentDBCLIException as e:
            logger.error(f"Failed to search skills: {e}")
            return []

    def consolidate_skills(self, min_attempts: int = 3, min_reward: float = 0.7,
                          time_window_days: int = 7) -> Optional[int]:
        """
        Consolidate episodes into skills.

        Args:
            min_attempts: Minimum number of attempts
            min_reward: Minimum reward threshold
            time_window_days: Time window in days

        Returns:
            Number of skills created if successful, None otherwise
        """
        try:
            command = [
                "skill", "consolidate",
                str(min_attempts),
                str(min_reward),
                str(time_window_days)
            ]

            result = self._run_agentdb_command(command)
            # Parse the output to get the number of skills created
            output = result.get("raw_output", "")
            for line in output.split('\n'):
                if "Created" in line and "skills" in line:
                    # Extract number from line like "Created 3 skills"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "Created" and i + 1 < len(parts):
                            try:
                                return int(parts[i + 1])
                            except ValueError:
                                break
            return 0

        except AgentDBCLIException as e:
            logger.error(f"Failed to consolidate skills: {e}")
            return None

    # Causal Memory Methods

    def add_causal_edge(self, edge: CausalEdge) -> Optional[int]:
        """
        Add a causal edge to AgentDB.

        Args:
            edge: Causal edge to add

        Returns:
            Edge ID if successful, None otherwise
        """
        try:
            command = [
                "causal", "add-edge",
                edge.cause,
                edge.effect,
                str(edge.uplift)
            ]

            if edge.confidence != 0.5:
                command.append(str(edge.confidence))
            if edge.sample_size:
                command.append(str(edge.sample_size))

            result = self._run_agentdb_command(command)
            return result.get("data", {}).get("edge_id")

        except AgentDBCLIException as e:
            logger.error(f"Failed to add causal edge: {e}")
            return None

    def query_causal_effects(self, cause: Optional[str] = None, effect: Optional[str] = None,
                           min_confidence: float = 0.0, min_uplift: float = 0.0,
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query causal effects from AgentDB.

        Args:
            cause: Cause to query
            effect: Effect to query
            min_confidence: Minimum confidence threshold
            min_uplift: Minimum uplift threshold
            limit: Maximum number of results

        Returns:
            List of causal edges
        """
        try:
            command = ["causal", "query"]

            if cause:
                command.append(cause)
            if effect:
                command.append(effect)
            command.extend([str(min_confidence), str(min_uplift), str(limit)])

            result = self._run_agentdb_command(command)
            # Parse causal edges from output
            return self._parse_causal_edges_output(result.get("raw_output", ""))

        except AgentDBCLIException as e:
            logger.error(f"Failed to query causal effects: {e}")
            return []

    def _parse_causal_edges_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse causal edges from AgentDB output"""
        edges = []
        lines = output.split('\n')

        for line in lines:
            if "→" in line and "uplift" in line.lower():
                # Parse line like: "use_template → agent_quality (uplift: 0.25, confidence: 0.95)"
                parts = line.split("→")
                if len(parts) >= 2:
                    cause = parts[0].strip()
                    effect_rest = parts[1]
                    effect = effect_rest.split("(")[0].strip()

                    # Extract uplift and confidence
                    uplift = 0.0
                    confidence = 0.0
                    if "uplift:" in effect_rest:
                        uplift_part = effect_rest.split("uplift:")[1].split(",")[0].strip()
                        try:
                            uplift = float(uplift_part)
                        except ValueError:
                            pass
                    if "confidence:" in effect_rest:
                        conf_part = effect_rest.split("confidence:")[1].split(")")[0].strip()
                        try:
                            confidence = float(conf_part)
                        except ValueError:
                            pass

                    edges.append({
                        "cause": cause,
                        "effect": effect,
                        "uplift": uplift,
                        "confidence": confidence
                    })

        return edges

    # Database Methods

    def get_database_stats(self) -> Dict[str, Any]:
        """Get AgentDB database statistics"""
        try:
            result = self._run_agentdb_command(["db", "stats"])
            return self._parse_database_stats(result.get("raw_output", ""))

        except AgentDBCLIException as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    def _parse_database_stats(self, output: str) -> Dict[str, Any]:
        """Parse database statistics from AgentDB output"""
        stats = {}
        lines = output.split('\n')

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key.startswith("causal_edges"):
                    try:
                        stats["causal_edges"] = int(value)
                    except ValueError:
                        pass
                elif key.startswith("episodes"):
                    try:
                        stats["episodes"] = int(value)
                    except ValueError:
                        pass
                elif key.startswith("causal_experiments"):
                    try:
                        stats["causal_experiments"] = int(value)
                    except ValueError:
                        pass

        return stats

    # Enhanced Methods for Agent-Creator Integration

    def enhance_agent_creation(self, user_input: str, domain: str = None) -> Dict[str, Any]:
        """
        Enhance agent creation using AgentDB real capabilities.

        This method integrates multiple AgentDB features to provide
        intelligent enhancement while maintaining the "invisible" experience.
        """
        enhancement = {
            "templates": [],
            "skills": [],
            "episodes": [],
            "causal_insights": [],
            "recommendations": []
        }

        if not self.is_available:
            return enhancement

        try:
            # 1. Search for relevant skills
            skills = self.search_skills(user_input, k=3, min_success_rate=0.7)
            enhancement["skills"] = skills

            # 2. Retrieve relevant episodes
            episodes = self.retrieve_episodes(user_input, k=5, min_reward=0.6)
            enhancement["episodes"] = episodes

            # 3. Query causal effects
            if domain:
                causal_effects = self.query_causal_effects(
                    cause=f"use_{domain}_template",
                    min_confidence=0.7,
                    min_uplift=0.1
                )
                enhancement["causal_insights"] = causal_effects

            # 4. Generate recommendations
            enhancement["recommendations"] = self._generate_recommendations(
                user_input, enhancement
            )

            logger.info(f"AgentDB enhancement completed: {len(skills)} skills, {len(episodes)} episodes")

        except Exception as e:
            logger.error(f"AgentDB enhancement failed: {e}")

        return enhancement

    def _generate_recommendations(self, user_input: str, enhancement: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on AgentDB data"""
        recommendations = []

        # Skill-based recommendations
        if enhancement["skills"]:
            recommendations.append(
                f"Found {len(enhancement['skills'])} relevant skills from AgentDB"
            )

        # Episode-based recommendations
        if enhancement["episodes"]:
            successful_episodes = [e for e in enhancement["episodes"] if e.get("success", False)]
            if successful_episodes:
                recommendations.append(
                    f"Found {len(successful_episodes)} successful similar attempts"
                )

        # Causal insights
        if enhancement["causal_insights"]:
            best_effect = max(enhancement["causal_insights"],
                            key=lambda x: x.get("uplift", 0),
                            default=None)
            if best_effect:
                recommendations.append(
                    f"Causal insight: {best_effect['cause']} improves {best_effect['effect']} by {best_effect['uplift']:.1%}"
                )

        return recommendations

# Global instance for backward compatibility
_agentdb_bridge = None

def get_real_agentdb_bridge(db_path: Optional[str] = None) -> RealAgentDBBridge:
    """Get the global real AgentDB bridge instance"""
    global _agentdb_bridge
    if _agentdb_bridge is None:
        _agentdb_bridge = RealAgentDBBridge(db_path)
    return _agentdb_bridge

def is_agentdb_available() -> bool:
    """Check if AgentDB is available"""
    try:
        bridge = get_real_agentdb_bridge()
        return bridge.is_available
    except:
        return False