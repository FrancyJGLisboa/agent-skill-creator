# Phase 6: Test Suite Generation (NEW v2.0!)

## Objective

**GENERATE** comprehensive test suite that validates ALL functions of the created skill.

**LEARNING:** us-crop-monitor v1.0 had ZERO tests. When expanding to v2.0, it was difficult to ensure nothing broke. v2.0 has 25 tests (100% passing) that ensure reliability.

---

## Why Are Tests Critical?

### Benefits for Developer:
- ✅ Ensures code works before distribution
- ✅ Detects bugs early (not after client installs!)
- ✅ Allows confident changes (regression testing)
- ✅ Documents expected behavior

### Benefits for Client:
- ✅ Confidence in skill ("100% tested")
- ✅ Fewer bugs in production
- ✅ More professional (commercially viable)

### Benefits for Agent-Creator:
- ✅ Validates that generated skill actually works
- ✅ Catch errors before considering "done"
- ✅ Automatic quality gate

---

## Test Structure

### tests/ Directory

```
{skill-name}/
└── tests/
    ├── test_fetch.py           # Tests API client
    ├── test_parse.py           # Tests parsers
    ├── test_analyze.py         # Tests analyses
    ├── test_integration.py     # Tests end-to-end
    ├── test_validation.py      # Tests validators
    ├── test_helpers.py         # Tests helpers (year detection, etc.)
    └── README.md               # How to run tests
```

---

## Template 1: test_fetch.py

**Objective:** Validate API client works

```python
#!/usr/bin/env python3
"""
Test suite for {API} client.

Tests all fetch methods with real API data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from fetch_{api} import {ApiClient}, DataNotFoundError


def test_get_{metric1}():
    """Test fetching {metric1} data."""
    print("\nTesting get_{metric1}()...")

    try:
        client = {ApiClient}()

        # Test with valid parameters
        result = client.get_{metric1}(
            {entity}='{valid_entity}',
            year=2024
        )

        # Validations
        assert 'data' in result, "Missing 'data' in result"
        assert 'metadata' in result, "Missing 'metadata'"
        assert len(result['data']) > 0, "No data returned"
        assert result['metadata']['from_cache'] in [True, False]

        print(f"  ✓ Fetched {len(result['data'])} records")
        print(f"  ✓ Metadata present")
        print(f"  ✓ From cache: {result['metadata']['from_cache']}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_get_{metric2}():
    """Test fetching {metric2} data."""
    # Similar structure...
    pass


def test_error_handling():
    """Test that errors are handled correctly."""
    print("\nTesting error handling...")

    try:
        client = {ApiClient}()

        # Test invalid entity (should raise)
        try:
            result = client.get_{metric1}({entity}='INVALID_ENTITY', year=2024)
            print("  ✗ Should have raised DataNotFoundError")
            return False
        except DataNotFoundError:
            print("  ✓ Correctly raises DataNotFoundError for invalid entity")

        # Test invalid year (should raise)
        try:
            result = client.get_{metric1}({entity}='{valid}', year=2099)
            print("  ✗ Should have raised ValidationError")
            return False
        except Exception as e:
            print(f"  ✓ Correctly raises error for future year")

        return True

    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False


def main():
    """Run all fetch tests."""
    print("=" * 70)
    print("FETCH TESTS - {API} Client")
    print("=" * 70)

    results = []

    # Test each get_* method
    results.append(("get_{metric1}", test_get_{metric1}()))
    results.append(("get_{metric2}", test_get_{metric2}()))
    # ... add test for ALL get_* methods

    results.append(("error_handling", test_error_handling()))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}()")

    print(f"\nResults: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

**Rule:** ONE test function for EACH `get_*()` method implemented!

---

## Template 2: test_parse.py

**Objective:** Validate parsers

```python
#!/usr/bin/env python3
"""
Test suite for data parsers.

Tests all parse_* modules.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from parse_{type1} import parse_{type1}_response
from parse_{type2} import parse_{type2}_response


def test_parse_{type1}():
    """Test {type1} parser."""
    print("\nTesting parse_{type1}_response()...")

    # Sample data (real structure from API)
    sample_data = [
        {
            'field1': 'value1',
            'field2': 'value2',
            'Value': '123',
            # ... real API fields
        }
    ]

    try:
        df = parse_{type1}_response(sample_data)

        # Validations
        assert not df.empty, "DataFrame is empty"
        assert 'Value' in df.columns or '{metric}_value' in df.columns
        assert len(df) == len(sample_data)

        print(f"  ✓ Parsed {len(df)} records")
        print(f"  ✓ Columns: {list(df.columns)}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parse_empty_data():
    """Test parser handles empty data gracefully."""
    print("\nTesting empty data handling...")

    try:
        from parse_{type1} import ParseError

        try:
            df = parse_{type1}_response([])
            print("  ✗ Should have raised ParseError")
            return False
        except ParseError as e:
            print(f"  ✓ Correctly raises ParseError: {e}")
            return True

    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False


def main():
    results = []

    # Test each parser
    results.append(("parse_{type1}", test_parse_{type1}()))
    results.append(("parse_{type2}", test_parse_{type2}()))
    # ... for ALL parsers

    results.append(("empty_data", test_parse_empty_data()))

    # Summary
    passed = sum(1 for _, r in results if r)
    print(f"\nResults: {passed}/{len(results)} passed")
    return passed == len(results)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
```

---

## Template 3: test_integration.py

**Objective:** End-to-end tests (MOST IMPORTANT!)

```python
#!/usr/bin/env python3
"""
Integration tests for {skill-name}.

Tests all analysis functions with REAL API data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from analyze_{domain} import (
    {function1},
    {function2},
    {function3},
    # ... import ALL functions
)


def test_{function1}():
    """Test {function1} with auto-year detection."""
    print("\n1. Testing {function1}()...")

    try:
        # Test WITHOUT year (auto-detection)
        result = {function1}({entity}='{valid_entity}')

        # Validations
        assert 'year' in result, "Missing year"
        assert 'year_requested' in result, "Missing year_requested"
        assert 'year_info' in result, "Missing year_info"
        assert result['year'] >= 2024, "Year too old"
        assert result['year_requested'] is None, "Should auto-detect"

        print(f"  ✓ Auto-year detection: {result['year']}")
        print(f"  ✓ Year info: {result['year_info']}")
        print(f"  ✓ Data present: {list(result.keys())}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_{function1}_with_explicit_year():
    """Test {function1} with explicit year."""
    print("\n2. Testing {function1}() with explicit year...")

    try:
        # Test WITH year specified
        result = {function1}({entity}='{valid_entity}', year=2024)

        assert result['year'] == 2024, f"Expected 2024, got {result['year']}"
        assert result['year_requested'] == 2024

        print(f"  ✓ Uses specified year: {result['year']}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_all_functions_exist():
    """Verify all expected functions are implemented."""
    print("\nVerifying all functions exist...")

    expected_functions = [
        '{function1}',
        '{function2}',
        '{function3}',
        # ... ALL functions
    ]

    missing = []
    for func_name in expected_functions:
        if func_name not in globals():
            missing.append(func_name)

    if missing:
        print(f"  ✗ Missing functions: {missing}")
        return False
    else:
        print(f"  ✓ All {len(expected_functions)} functions present")
        return True


def main():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("{SKILL NAME} - INTEGRATION TEST SUITE")
    print("=" * 70)

    results = []

    # Test each function
    results.append(("{function1} auto-year", test_{function1}()))
    results.append(("{function1} explicit-year", test_{function1}_with_explicit_year()))
    # ... repeat for ALL functions

    results.append(("all_functions_exist", test_all_functions_exist()))

    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\n✓ Passed: {passed}/{total}")
    print(f"✗ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! SKILL IS PRODUCTION READY!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed - FIX BEFORE RELEASE")

    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

**Rule:** Minimum 2 tests per analysis function (auto-year + explicit-year)

---

## Template 4: test_helpers.py

**Objective:** Test year detection helpers

```python
#!/usr/bin/env python3
"""
Test suite for utility helpers.

Tests temporal context detection.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from utils.helpers import (
    get_current_{domain}_year,
    should_try_previous_year,
    format_year_message
)


def test_get_current_year():
    """Test current year detection."""
    print("\nTesting get_current_{domain}_year()...")

    try:
        year = get_current_{domain}_year()
        current_year = datetime.now().year

        assert year == current_year, f"Expected {current_year}, got {year}"

        print(f"  ✓ Correctly returns: {year}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_should_try_previous_year():
    """Test seasonal fallback logic."""
    print("\nTesting should_try_previous_year()...")

    try:
        # Test with None (current year)
        result = should_try_previous_year()
        print(f"  ✓ Current year fallback: {result}")

        # Test with specific year
        result_past = should_try_previous_year(2023)
        print(f"  ✓ Past year fallback: {result_past}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_format_year_message():
    """Test year message formatting."""
    print("\nTesting format_year_message()...")

    try:
        # Test auto-detected
        msg1 = format_year_message(2025, None)
        assert "auto-detected" in msg1.lower() or "2025" in msg1
        print(f"  ✓ Auto-detected: {msg1}")

        # Test requested
        msg2 = format_year_message(2024, 2024)
        assert "2024" in msg2
        print(f"  ✓ Requested: {msg2}")

        # Test fallback
        msg3 = format_year_message(2024, 2025)
        assert "not" in msg3.lower() or "fallback" in msg3.lower()
        print(f"  ✓ Fallback: {msg3}")

        return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def main():
    results = []

    results.append(("get_current_year", test_get_current_year()))
    results.append(("should_try_previous_year", test_should_try_previous_year()))
    results.append(("format_year_message", test_format_year_message()))

    passed = sum(1 for _, r in results if r)
    print(f"\nResults: {passed}/{len(results)} passed")

    return passed == len(results)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
```

---

## Quality Rules for Tests

### 1. ALL tests must use REAL DATA

❌ **FORBIDDEN:**
```python
def test_function():
    # Mock data
    mock_data = {'fake': 'data'}
    result = function(mock_data)
    assert result == 'expected'
```

✅ **MANDATORY:**
```python
def test_function():
    # Real API call
    client = ApiClient()
    result = client.get_real_data(entity='REAL', year=2024)

    # Validate real response
    assert len(result['data']) > 0
    assert 'metadata' in result
```

**Why?**
- Tests with mocks don't guarantee API is working
- Real tests detect API changes
- Client needs to know it works with REAL data

---

### 2. Tests must be FAST

**Goal:** Complete suite in < 60 seconds

**Techniques:**
- Use cache: First test populates cache, rest use cached
- Limit requests: Don't test 100 entities, test 2-3
- Parallel where possible

```python
# Example: Populate cache once
@classmethod
def setUpClass(cls):
    """Populate cache before all tests."""
    client = ApiClient()
    client.get_data('ENTITY1', 2024)  # Cache for other tests

# Tests then use cached data (fast)
```

---

### 3. Tests must PASS 100%

**Quality Gate:** Skill is only "done" when ALL tests pass.

```python
if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ SKILL NOT READY - FIX FAILING TESTS")
        sys.exit(1)
    else:
        print("\n✅ SKILL READY FOR DISTRIBUTION")
        sys.exit(0)
```

---

## Test Coverage Requirements

### Minimum Mandatory:

**Per module:**
- `fetch_{api}.py`: 1 test per `get_*()` method + 1 error handling test
- Each `parse_{type}.py`: 1 test per main function
- `analyze_{domain}.py`: 2 tests per analysis (auto-year + explicit-year)
- `utils/helpers.py`: 3 tests (get_year, should_fallback, format_message)

**Expected total:** 15-30 tests depending on skill size

**Example (us-crop-monitor v2.0):**
- test_fetch.py: 6 tests (5 get_* + 1 error)
- test_parse.py: 4 tests (4 parsers)
- test_analyze.py: 11 tests (11 functions)
- test_helpers.py: 3 tests
- test_integration.py: 1 end-to-end test
- **Total:** 25 tests

---

## How to Run Tests

### Individual:
```bash
python3 tests/test_fetch.py
python3 tests/test_integration.py
```

### Complete suite:
```bash
# Run all
for test in tests/test_*.py; do
    python3 $test || exit 1
done

# Or with pytest (if available)
pytest tests/
```

### In CI/CD:
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install -r requirements.txt
      - run: python3 tests/test_integration.py
```

---

## Output Example

**When tests pass:**
```
======================================================================
US CROP MONITOR - INTEGRATION TEST SUITE
======================================================================

1. current_condition_report()...
   ✓ Year: 2025 | Week: 39
   ✓ Good+Excellent: 66.0%

2. week_over_week_comparison()...
   ✓ Year: 2025 | Weeks: 39 vs 38
   ✓ Delta: -2.2 pts

...

======================================================================
FINAL SUMMARY
======================================================================

✓ Passed: 25/25 tests
✗ Failed: 0/25 tests

🎉 ALL TESTS PASSED! SKILL IS PRODUCTION READY!
======================================================================
```

**When tests fail:**
```
8. yield_analysis()...
   ✗ FAILED: 'yield_bu_per_acre' not in result

...

FINAL SUMMARY:
✓ Passed: 24/25
✗ Failed: 1/25

❌ SKILL NOT READY - FIX FAILING TESTS
```

---

## Integration with Agent-Creator

### When to generate tests:

**In Phase 5 (Implementation):**

Updated order:
```
...
8. Implement analyze (analyses)
9. CREATE TESTS (← here!)
   - Generate test_fetch.py
   - Generate test_parse.py
   - Generate test_analyze.py
   - Generate test_helpers.py
   - Generate test_integration.py
10. RUN TESTS
    - Run test suite
    - If fails → FIX and re-run
    - Only continue when 100% passing
11. Create examples/
...
```

### Quality Gate:

```python
# Agent-creator should do:
print("Running test suite...")
exit_code = subprocess.run(['python3', 'tests/test_integration.py']).returncode

if exit_code != 0:
    print("❌ Tests failed - aborting skill generation")
    print("Fix errors above and try again")
    sys.exit(1)

print("✅ All tests passed - continuing...")
```

---

## Testing Checklist

Before considering skill "done":

- [ ] tests/ directory created
- [ ] test_fetch.py with 1 test per get_*() method
- [ ] test_parse.py with 1 test per parser
- [ ] test_analyze.py with 2 tests per function (auto-year + explicit)
- [ ] test_helpers.py with year detection tests
- [ ] test_integration.py with end-to-end test
- [ ] ALL tests passing (100%)
- [ ] Test suite executes in < 60 seconds
- [ ] README in tests/ explaining how to run

---

## Real Example: us-crop-monitor v2.0

**Tests created:**
- `test_new_metrics.py` - 5 tests (fetch methods)
- `test_year_detection.py` - 2 tests (auto-detection)
- `test_all_year_detection.py` - 4 tests (all functions)
- `test_new_analyses.py` - 3 tests (new analyses)
- `tests/test_integrated_validation.py` - 11 tests (comprehensive)

**Total:** 25 tests, 100% passing

**Result:**
```
✓ Passed: 25/25 tests
🎉 ALL TESTS PASSED! SKILL IS PRODUCTION READY!
```

**Benefit:** Full confidence v2.0 works before distribution!

---

## Conclusion

**ALWAYS generate test suite!**

Skills without tests = prototypes
Skills with tests = professional products ✅

**ROI:** Tests cost +2h to create, but save 10-20h of debugging later!
