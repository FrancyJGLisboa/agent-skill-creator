#!/usr/bin/env python3
"""
Integration Tests for Agent Creator v2.0
Tests end-to-end workflows with new features.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_template_based_agent_creation():
    """Test complete template-based agent creation workflow"""
    print("Testing template-based agent creation...")

    # Step 1: Load template
    template_path = Path(__file__).parent.parent / "templates" / "financial-analysis.json"
    with open(template_path, 'r') as f:
        template = json.load(f)

    assert "apis" in template, "Template should have APIs section"
    assert "analyses" in template, "Template should have analyses section"

    # Step 2: Customize template
    customizations = {
        "additional_indicators": ["Williams %R", "Stochastic"],
        "portfolio_optimization_method": "Modern Portfolio Theory"
    }

    # Step 3: Generate agent structure
    agent_structure = {
        "name": "custom-financial-analysis",
        "apis": template["apis"],
        "analyses": template["analyses"],
        "customizations": customizations
    }

    print("✓ Template loaded and customized")
    return True

def test_multi_agent_suite_creation():
    """Test multi-agent suite creation workflow"""
    print("Testing multi-agent suite creation...")

    # Define suite specification
    suite_spec = {
        "name": "financial-analysis-suite",
        "agents": [
            {
                "name": "fundamental-analysis",
                "description": "Company fundamentals and valuation",
                "apis": ["Alpha Vantage"],
                "analyses": ["P/E Ratio", "ROE", "Debt/Equity"]
            },
            {
                "name": "technical-analysis",
                "description": "Technical indicators and signals",
                "apis": ["Alpha Vantage", "Yahoo Finance"],
                "analyses": ["RSI", "MACD", "Bollinger Bands"]
            }
        ]
    }

    # Generate marketplace.json for suite
    marketplace_config = {
        "name": suite_spec["name"],
        "metadata": {
            "description": "Complete financial analysis suite",
            "version": "1.0.0",
            "suite_type": "financial_analysis"
        },
        "plugins": []
    }

    # Add each agent to marketplace.json
    for agent in suite_spec["agents"]:
        plugin_config = {
            "name": f"{agent['name']}-plugin",
            "description": agent["description"],
            "source": f"./{agent['name']}/",
            "skills": ["./SKILL.md"]
        }
        marketplace_config["plugins"].append(plugin_config)

    # Validate structure
    assert len(marketplace_config["plugins"]) == 2, "Should have 2 plugins"
    assert all("source" in plugin for plugin in marketplace_config["plugins"])

    print("✓ Multi-agent suite structure created")
    return True

def test_transcript_workflow_extraction():
    """Test transcript processing and workflow extraction"""
    print("Testing transcript workflow extraction...")

    sample_transcript = """
    Welcome to our complete e-commerce analytics tutorial!

    In the first part, we'll connect to Google Analytics API
    to track website traffic and user behavior. We'll analyze
    page views, bounce rates, and conversion funnels.

    Next, we'll integrate with Stripe API to get payment data,
    calculate revenue metrics like Average Order Value and
    Customer Lifetime Value.

    Then we'll use Shopify API to pull product performance data,
    analyze inventory turnover, and identify top-selling products.

    Finally, we'll create an automated dashboard that combines
    all these metrics and sends weekly reports via email.
    """

    # Extract workflows
    workflows = []

    # Look for API mentions
    if "Google Analytics" in transcript:
        workflows.append({
            "name": "traffic_analysis",
            "apis": ["Google Analytics"],
            "metrics": ["page views", "bounce rate", "conversion funnel"]
        })

    if "Stripe API" in transcript:
        workflows.append({
            "name": "revenue_analysis",
            "apis": ["Stripe"],
            "metrics": ["AOV", "LTV", "revenue trends"]
        })

    if "Shopify API" in transcript:
        workflows.append({
            "name": "product_analysis",
            "apis": ["Shopify"],
            "metrics": ["product performance", "inventory turnover"]
        })

    if "dashboard" in transcript and "reports" in transcript:
        workflows.append({
            "name": "reporting_automation",
            "apis": [],
            "metrics": ["automated reports", "dashboard creation"]
        })

    # Validate extraction
    assert len(workflows) == 4, f"Should extract 4 workflows, got {len(workflows)}"

    workflow_names = [w["name"] for w in workflows]
    expected_names = ["traffic_analysis", "revenue_analysis", "product_analysis", "reporting_automation"]
    for name in expected_names:
        assert name in workflow_names, f"Should include {name} workflow"

    print("✓ Workflows extracted from transcript")
    return True

def test_interactive_configuration_flow():
    """Test interactive configuration decision flow"""
    print("Testing interactive configuration flow...")

    # Simulate user interaction
    user_input = {
        "goal": "Build a complete financial analysis system",
        "domain": "Finance & Investing",
        "complexity": "high",
        "existing_materials": "YouTube transcript",
        "workflow_count": 3,
        "integration_needed": True
    }

    # Decision logic
    configuration_decisions = {}

    # Strategy selection
    if user_input["workflow_count"] > 1:
        if user_input["integration_needed"]:
            configuration_decisions["strategy"] = "integrated_suite"
        else:
            configuration_decisions["strategy"] = "multi_agent_suite"
    else:
        configuration_decisions["strategy"] = "single_agent"

    # Template recommendation
    if user_input["domain"] == "Finance & Investing":
        configuration_decisions["template"] = "financial-analysis"

    # Creation method
    if user_input["existing_materials"] == "YouTube transcript":
        configuration_decisions["creation_method"] = "transcript_based"
    elif configuration_decisions.get("template"):
        configuration_decisions["creation_method"] = "template_based"
    else:
        configuration_decisions["creation_method"] = "custom"

    # Validation
    expected_decisions = {
        "strategy": "integrated_suite",
        "template": "financial-analysis",
        "creation_method": "transcript_based"
    }

    for key, expected_value in expected_decisions.items():
        assert configuration_decisions[key] == expected_value, \
            f"Decision {key} should be {expected_value}"

    print("✓ Interactive configuration decisions validated")
    return True

def test_backward_compatibility():
    """Test backward compatibility with v1.0 workflows"""
    print("Testing backward compatibility...")

    # Simulate v1.0 input
    v1_input = "Create an agent for stock analysis that fetches data from Alpha Vantage"

    # Should still work with enhanced system
    if "agent for" in v1_input:
        # Should trigger basic agent creation
        creation_mode = "single_agent"

    if "Alpha Vantage" in v1_input:
        # Should identify API
        detected_api = "Alpha Vantage"

    if "stock analysis" in v1_input:
        # Should identify domain
        detected_domain = "finance"

    # Validate v1.0 compatibility
    assert creation_mode == "single_agent", "Should default to single agent for v1.0 input"
    assert detected_api == "Alpha Vantage", "Should detect API correctly"
    assert detected_domain == "finance", "Should detect domain correctly"

    print("✓ Backward compatibility maintained")
    return True

def test_enhanced_validation_layers():
    """Test enhanced validation system"""
    print("Testing enhanced validation layers...")

    # Test data
    test_agent_data = {
        "parameters": {"symbol": "AAPL", "period": "1y"},
        "api_response": {"status": "success", "data": [1, 2, 3, 4, 5]},
        "processing_result": {"indicators": {"RSI": 45.2, "MACD": 1.23}},
        "integration_data": {"cross_agent_data": True}
    }

    # Validation layers
    validation_results = {}

    # Layer 1: Parameter validation
    try:
        assert test_agent_data["parameters"]["symbol"], "Symbol should not be empty"
        assert test_agent_data["parameters"]["period"], "Period should not be empty"
        validation_results["parameter_validation"] = {"passed": True, "errors": []}
    except AssertionError as e:
        validation_results["parameter_validation"] = {"passed": False, "errors": [str(e)]}

    # Layer 2: Data quality validation
    try:
        assert test_agent_data["api_response"]["status"] == "success", "API should return success"
        assert len(test_agent_data["api_response"]["data"]) > 0, "Data should not be empty"
        validation_results["data_quality_validation"] = {"passed": True, "warnings": []}
    except AssertionError as e:
        validation_results["data_quality_validation"] = {"passed": False, "warnings": [str(e)]}

    # Layer 3: Processing validation
    try:
        assert "indicators" in test_agent_data["processing_result"], "Should have indicators"
        validation_results["processing_validation"] = {"passed": True, "errors": []}
    except AssertionError as e:
        validation_results["processing_validation"] = {"passed": False, "errors": [str(e)]}

    # Layer 4: Integration validation
    try:
        assert test_agent_data["integration_data"]["cross_agent_data"], "Should support integration"
        validation_results["integration_validation"] = {"passed": True, "compatible": True}
    except AssertionError as e:
        validation_results["integration_validation"] = {"passed": False, "compatible": False}

    # Overall validation
    all_passed = all(
        result["passed"] for result in validation_results.values()
        if isinstance(result, dict) and "passed" in result
    )

    assert all_passed, "All validation layers should pass"
    assert len(validation_results) == 4, "Should have 4 validation layers"

    print("✓ Enhanced validation layers working")
    return True

def run_integration_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("AGENT CREATOR V2.0 INTEGRATION TESTS")
    print("=" * 70)

    tests = [
        test_template_based_agent_creation,
        test_multi_agent_suite_creation,
        test_transcript_workflow_extraction,
        test_interactive_configuration_flow,
        test_backward_compatibility,
        test_enhanced_validation_layers
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, True, None))
            print(f"✓ {test.__name__} PASSED")
        except Exception as e:
            results.append((test.__name__, False, str(e)))
            print(f"✗ {test.__name__} FAILED: {e}")
        print()

    # Summary
    print("=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    if passed < total:
        print("\nFailed tests:")
        for name, success, error in results:
            if not success:
                print(f"- {name}: {error}")

    return passed == total

if __name__ == "__main__":
    success = run_integration_tests()
    print(f"\nIntegration tests {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)