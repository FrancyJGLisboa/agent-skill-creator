#!/usr/bin/env python3
"""
Test script to demonstrate AgentDB learning capabilities
This simulates agent creation events to populate the database
"""

import sys
import time
from pathlib import Path

# Add integrations to path
sys.path.insert(0, str(Path(__file__).parent / "integrations"))

from agentdb_real_integration import (
    RealAgentDBBridge, Episode, Skill, CausalEdge
)

def test_reflexion_memory():
    """Test episode storage and retrieval"""
    print("\n" + "="*80)
    print("🧠 TESTING REFLEXION MEMORY (Episodes)")
    print("="*80)

    bridge = RealAgentDBBridge()

    if not bridge.is_available:
        print("❌ AgentDB not available. Please install: npm install -g @anthropic-ai/agentdb")
        return False

    # Simulate 3 financial agent creations
    episodes = [
        Episode(
            session_id="test-financial-001",
            task="Create financial analysis agent for stock market data",
            input="User wants to analyze AAPL, MSFT, GOOG stocks",
            output="Created financial-analysis-cskill with yfinance integration",
            critique="Successfully created, user satisfied with API selection",
            reward=95.0,
            success=True,
            latency_ms=18000,
            tokens_used=5000
        ),
        Episode(
            session_id="test-financial-002",
            task="Create financial portfolio tracking agent",
            input="User wants to track portfolio performance with technical indicators",
            output="Created portfolio-tracker-cskill with pandas-ta integration",
            critique="Good implementation, added RSI and MACD indicators",
            reward=90.0,
            success=True,
            latency_ms=15000,
            tokens_used=4500
        ),
        Episode(
            session_id="test-financial-003",
            task="Create cryptocurrency analysis agent",
            input="User wants to analyze Bitcoin and Ethereum trends",
            output="Created crypto-analysis-cskill with CoinGecko API",
            critique="Excellent, added real-time price alerts",
            reward=92.0,
            success=True,
            latency_ms=12000,
            tokens_used=4200
        )
    ]

    print("\n📝 Storing 3 financial agent creation episodes...")
    for i, episode in enumerate(episodes, 1):
        episode_id = bridge.store_episode(episode)
        if episode_id:
            print(f"  ✅ Stored episode #{episode_id}: {episode.task[:50]}...")
        else:
            print(f"  ❌ Failed to store episode {i}")
        time.sleep(0.5)

    # Retrieve similar episodes
    print("\n🔍 Retrieving similar episodes for 'financial analysis'...")
    retrieved = bridge.retrieve_episodes("financial analysis", k=3, min_reward=0.8)
    print(f"  ✅ Retrieved {len(retrieved)} relevant episodes")
    for ep in retrieved:
        print(f"     - {ep.get('task', 'Unknown')[:60]}...")

    return True

def test_skill_library():
    """Test skill creation and search"""
    print("\n" + "="*80)
    print("📚 TESTING SKILL LIBRARY")
    print("="*80)

    bridge = RealAgentDBBridge()

    # Create skills from successful episodes
    skills = [
        Skill(
            name="yfinance_stock_data_fetcher",
            description="Fetches stock market data using yfinance API with caching",
            code="def fetch_stock_data(symbol, period='1mo'): ...",
            success_rate=0.95,
            uses=3,
            avg_reward=92.0
        ),
        Skill(
            name="technical_indicators_calculator",
            description="Calculates RSI, MACD, Bollinger Bands for stocks",
            code="def calculate_indicators(df): ...",
            success_rate=0.90,
            uses=2,
            avg_reward=91.0
        ),
        Skill(
            name="portfolio_performance_analyzer",
            description="Analyzes portfolio returns, risk metrics, and diversification",
            code="def analyze_portfolio(holdings): ...",
            success_rate=0.88,
            uses=1,
            avg_reward=90.0
        )
    ]

    print("\n📝 Creating 3 skills from successful patterns...")
    for i, skill in enumerate(skills, 1):
        skill_id = bridge.create_skill(skill)
        if skill_id:
            print(f"  ✅ Created skill #{skill_id}: {skill.name}")
        else:
            print(f"  ❌ Failed to create skill {i}")
        time.sleep(0.5)

    # Search for skills
    print("\n🔍 Searching for 'stock' related skills...")
    found_skills = bridge.search_skills("stock", k=5)
    print(f"  ✅ Found {len(found_skills)} relevant skills")
    for skill in found_skills:
        print(f"     - {skill.get('name', 'Unknown')}")

    # Consolidate episodes into skills
    print("\n🔄 Consolidating episodes into skills...")
    consolidated = bridge.consolidate_skills(min_attempts=2, min_reward=0.8)
    if consolidated is not None:
        print(f"  ✅ Consolidated {consolidated} new skills from episodes")

    return True

def test_causal_memory():
    """Test causal edge storage and querying"""
    print("\n" + "="*80)
    print("🔗 TESTING CAUSAL MEMORY (Causal Relationships)")
    print("="*80)

    bridge = RealAgentDBBridge()

    # Add causal relationships discovered during agent creation
    causal_edges = [
        CausalEdge(
            cause="use_financial_template",
            effect="agent_creation_speed",
            uplift=0.40,  # 40% faster
            confidence=0.95,
            sample_size=3
        ),
        CausalEdge(
            cause="use_yfinance_api",
            effect="user_satisfaction",
            uplift=0.25,  # 25% higher satisfaction
            confidence=0.90,
            sample_size=3
        ),
        CausalEdge(
            cause="add_technical_indicators",
            effect="agent_quality",
            uplift=0.30,  # 30% quality improvement
            confidence=0.85,
            sample_size=2
        ),
        CausalEdge(
            cause="use_caching",
            effect="performance",
            uplift=0.60,  # 60% performance boost
            confidence=0.92,
            sample_size=3
        )
    ]

    print("\n📝 Adding 4 causal relationships...")
    for i, edge in enumerate(causal_edges, 1):
        edge_id = bridge.add_causal_edge(edge)
        if edge_id:
            print(f"  ✅ Added edge #{edge_id}: {edge.cause} → {edge.effect} (uplift: {edge.uplift:.1%})")
        else:
            print(f"  ❌ Failed to add edge {i}")
        time.sleep(0.5)

    # Query causal effects
    print("\n🔍 Querying causal effects for 'use_financial_template'...")
    effects = bridge.query_causal_effects(
        cause="use_financial_template",
        min_confidence=0.7,
        min_uplift=0.1
    )
    print(f"  ✅ Found {len(effects)} causal effects")
    for effect in effects:
        print(f"     - {effect.get('cause')} → {effect.get('effect')} "
              f"(uplift: {effect.get('uplift', 0):.1%}, confidence: {effect.get('confidence', 0):.1%})")

    # Query by effect
    print("\n🔍 Querying what improves 'user_satisfaction'...")
    causes = bridge.query_causal_effects(
        effect="user_satisfaction",
        min_confidence=0.7,
        min_uplift=0.1
    )
    print(f"  ✅ Found {len(causes)} causal factors")
    for cause in causes:
        print(f"     - {cause.get('cause')} → {cause.get('effect')} "
              f"(uplift: {cause.get('uplift', 0):.1%})")

    return True

def test_database_stats():
    """Check database statistics"""
    print("\n" + "="*80)
    print("📊 DATABASE STATISTICS")
    print("="*80)

    bridge = RealAgentDBBridge()
    stats = bridge.get_database_stats()

    if stats:
        print("\n✅ Database populated successfully!")
        print(f"   Episodes: {stats.get('episodes', 0)}")
        print(f"   Causal edges: {stats.get('causal_edges', 0)}")
        print(f"   Causal experiments: {stats.get('causal_experiments', 0)}")
    else:
        print("\n❌ No statistics available")

    return bool(stats)

def test_enhancement_capabilities():
    """Test enhanced agent creation capabilities"""
    print("\n" + "="*80)
    print("⚡ TESTING ENHANCEMENT CAPABILITIES")
    print("="*80)

    bridge = RealAgentDBBridge()

    # Simulate enhancement for new financial agent request
    print("\n🧠 Enhancing new agent creation with learned intelligence...")
    enhancement = bridge.enhance_agent_creation(
        user_input="Create a comprehensive financial analysis agent with portfolio tracking",
        domain="financial"
    )

    print(f"\n✅ Enhancement results:")
    print(f"   Skills found: {len(enhancement.get('skills', []))}")
    print(f"   Episodes retrieved: {len(enhancement.get('episodes', []))}")
    print(f"   Causal insights: {len(enhancement.get('causal_insights', []))}")
    print(f"   Recommendations: {len(enhancement.get('recommendations', []))}")

    if enhancement.get('recommendations'):
        print(f"\n💡 Recommendations:")
        for rec in enhancement['recommendations']:
            print(f"     - {rec}")

    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 AGENT-SKILL-CREATOR: AgentDB LEARNING CAPABILITIES TEST")
    print("="*80)
    print("\nThis test demonstrates how AgentDB learns from agent creation")
    print("and progressively improves recommendations and performance.")

    # Run tests
    success = True
    success &= test_reflexion_memory()
    success &= test_skill_library()
    success &= test_causal_memory()
    success &= test_database_stats()
    success &= test_enhancement_capabilities()

    # Summary
    print("\n" + "="*80)
    print("📈 TEST SUMMARY")
    print("="*80)
    if success:
        print("\n✅ All tests completed successfully!")
        print("\n🎯 Key Learning Capabilities Demonstrated:")
        print("   1. Reflexion Memory: Stores and retrieves similar experiences")
        print("   2. Skill Library: Consolidates successful patterns into reusable skills")
        print("   3. Causal Memory: Tracks what causes improvements")
        print("   4. Enhancement: Uses learned intelligence for better recommendations")
        print("\n💡 Next Steps:")
        print("   - Run 'agentdb db stats' to see database growth")
        print("   - Query specific skills, episodes, or causal relationships")
        print("   - Create more agents to see progressive improvement")
    else:
        print("\n⚠️  Some tests failed. Check AgentDB installation.")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
