#!/usr/bin/env python3
"""
Test AgentDB Real Integration

This script tests the integration with real AgentDB CLI to validate
that the bridge layer works correctly.
"""

import sys
import os
import logging
from pathlib import Path

# Add the integrations directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "integrations"))

from agentdb_bridge import get_agentdb_bridge
from agentdb_real_integration import get_real_agentdb_bridge, Episode, Skill, CausalEdge

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_original_bridge():
    """Test the original AgentDB bridge"""
    print("\n🔍 Testing Original AgentDB Bridge...")

    try:
        bridge = get_agentdb_bridge()
        print(f"✅ Bridge initialized")
        print(f"   Available: {bridge.is_available}")
        print(f"   Configured: {bridge.is_configured}")

        if bridge.is_available:
            # Test enhancement
            intelligence = bridge.enhance_agent_creation(
                "Create financial analysis agent for stock market data",
                "finance"
            )

            print(f"✅ Enhancement completed:")
            print(f"   Template choice: {intelligence.template_choice}")
            print(f"   Success probability: {intelligence.success_probability:.2%}")
            print(f"   Learned improvements: {len(intelligence.learned_improvements)}")
            for improvement in intelligence.learned_improvements[:3]:
                print(f"     - {improvement}")
        else:
            print("⚠️  AgentDB not available - using fallback mode")

    except Exception as e:
        print(f"❌ Original bridge test failed: {e}")
        return False

    return True

def test_real_agentdb_integration():
    """Test the real AgentDB integration"""
    print("\n🔍 Testing Real AgentDB Integration...")

    try:
        bridge = get_real_agentdb_bridge()
        print(f"✅ Real bridge initialized")
        print(f"   Available: {bridge.is_available}")

        if bridge.is_available:
            # Test storing an episode
            episode = Episode(
                session_id="test-session-001",
                task="create_financial_agent",
                input="User wants financial analysis",
                output="Created financial agent with APIs",
                critique="Used Alpha Vantage API successfully",
                reward=0.85,
                success=True,
                latency_ms=2000,
                tokens_used=1500
            )

            episode_id = bridge.store_episode(episode)
            print(f"✅ Episode stored: #{episode_id}")

            # Test retrieving episodes
            episodes = bridge.retrieve_episodes("financial_agent", k=3, min_reward=0.6)
            print(f"✅ Episodes retrieved: {len(episodes)}")
            for ep in episodes:
                print(f"   - {ep.get('task', 'unknown')} (reward: {ep.get('reward', 0):.2f})")

            # Test creating a skill
            skill = Skill(
                name="financial_analysis_enhanced",
                description="Enhanced financial analysis with real-time data",
                code="Use Alpha Vantage + Yahoo Finance APIs",
                success_rate=0.9,
                uses=1,
                avg_reward=0.85
            )

            skill_id = bridge.create_skill(skill)
            print(f"✅ Skill created: #{skill_id}")

            # Test searching skills
            skills = bridge.search_skills("financial", k=3, min_success_rate=0.7)
            print(f"✅ Skills found: {len(skills)}")
            for skill in skills:
                print(f"   - {skill.get('name', 'unknown')} (success: {skill.get('success_rate', 0):.1%})")

            # Test adding causal edge
            edge = CausalEdge(
                cause="use_real_apis",
                effect="agent_accuracy",
                uplift=0.3,
                confidence=0.9,
                sample_size=50,
                mechanism="Real-time data improves analysis accuracy"
            )

            edge_id = bridge.add_causal_edge(edge)
            print(f"✅ Causal edge added: #{edge_id}")

            # Test database stats
            stats = bridge.get_database_stats()
            print(f"✅ Database stats: {stats}")

            # Test enhancement
            enhancement = bridge.enhance_agent_creation(
                "Create financial analysis agent with real-time data",
                "finance"
            )

            print(f"✅ Enhancement completed:")
            print(f"   Skills found: {len(enhancement['skills'])}")
            print(f"   Episodes found: {len(enhancement['episodes'])}")
            print(f"   Causal insights: {len(enhancement['causal_insights'])}")
            print(f"   Recommendations: {len(enhancement['recommendations'])}")

            for rec in enhancement['recommendations']:
                print(f"     - {rec}")

        else:
            print("⚠️  Real AgentDB not available")

    except Exception as e:
        print(f"❌ Real AgentDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def test_direct_agentdb_commands():
    """Test direct AgentDB CLI commands"""
    print("\n🔍 Testing Direct AgentDB Commands...")

    try:
        import subprocess

        # Test database stats
        result = subprocess.run(
            ["agentdb", "db", "stats"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ Database stats command successful")
            print("   Output preview:")
            lines = result.stdout.strip().split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"     {line}")
        else:
            print(f"❌ Database stats command failed: {result.stderr}")
            return False

        # Test storing an episode
        result = subprocess.run([
            "agentdb", "reflexion", "store",
            "test-direct-session",
            "test_task",
            "0.9",
            "true",
            "Direct test episode"
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Direct episode store successful")
        else:
            print(f"❌ Direct episode store failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Direct commands test failed: {e}")
        return False

    return True

def main():
    """Run all tests"""
    print("🚀 Starting AgentDB Integration Tests")
    print("=" * 50)

    tests = [
        ("Direct AgentDB Commands", test_direct_agentdb_commands),
        ("Real AgentDB Integration", test_real_agentdb_integration),
        ("Original AgentDB Bridge", test_original_bridge),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅ PASSED' if success else '❌ FAILED'}: {test_name}")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*50}")
    print("🏁 Test Results Summary:")
    print("=" * 50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! AgentDB integration is working.")
    else:
        print("⚠️  Some tests failed. Check the logs above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)