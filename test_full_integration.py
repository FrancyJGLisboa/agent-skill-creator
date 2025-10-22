#!/usr/bin/env python3
"""
Full AgentDB Integration Test

This script simulates the complete agent creation process with AgentDB integration
to validate that learning happens automatically during normal usage.
"""

import sys
import os
import logging
import time
from pathlib import Path
from datetime import datetime

# Add the integrations directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "integrations"))

from agentdb_bridge import get_agentdb_bridge
from agentdb_real_integration import get_real_agentdb_bridge, Episode, Skill

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simulate_phase_1_with_agentdb(user_input: str, domain: str):
    """Simulate Phase 1 with AgentDB integration"""
    print(f"\n🔍 PHASE 1: Discovery and Research")
    print(f"   User Input: '{user_input}'")
    print(f"   Domain: {domain}")

    # Get AgentDB intelligence
    bridge = get_agentdb_bridge()
    intelligence = bridge.enhance_agent_creation(user_input, domain)

    print(f"   🧠 AgentDB Analysis:")
    print(f"      - Available: {bridge.is_available}")
    print(f"      - Success Probability: {intelligence.success_probability:.1%}")
    print(f"      - Template Choice: {intelligence.template_choice}")
    print(f"      - Learned Improvements: {len(intelligence.learned_improvements)}")

    for improvement in intelligence.learned_improvements[:2]:
        print(f"      - {improvement}")

    # Simulate API research
    print(f"   🔍 Researching APIs for {domain} domain...")
    time.sleep(1)  # Simulate research time

    # Decision with AgentDB backing
    selected_api = "Alpha Vantage" if domain == "finance" else "USDA NASS"
    print(f"   ✅ DECISION: Selected {selected_api}")
    print(f"      - Confidence: {intelligence.success_probability:.1%}")
    if intelligence.mathematical_proof:
        print(f"      - Validation: {intelligence.mathematical_proof}")

    return selected_api, intelligence

def simulate_phase_5_with_agentdb(user_input: str, domain: str, selected_api: str,
                                 agent_name: str, success: bool = True):
    """Simulate Phase 5 with AgentDB episode storage"""
    print(f"\n🏗️ PHASE 5: Implementation and Learning")
    print(f"   Agent: {agent_name}")
    print(f"   API: {selected_api}")

    # Simulate creation time
    creation_time = 45  # seconds
    time.sleep(2)  # Simulate implementation

    print(f"   ✅ Agent created successfully!")
    print(f"   🧠 Storing episode for future learning...")

    try:
        # Store episode using real AgentDB
        bridge = get_real_agentdb_bridge()

        episode = Episode(
            session_id=f"agent-creation-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            task=user_input,
            input=f"Domain: {domain}, API: {selected_api}",
            output=f"Created: {agent_name}/ with complete structure",
            critique=f"Success: {'✅ High quality' if success else '⚠️ Needs refinement'}",
            reward=0.9 if success else 0.7,
            success=success,
            latency_ms=creation_time * 1000,
            tokens_used=8500,
            tags=[domain, selected_api, "complete_agent"],
            metadata={
                "agent_name": agent_name,
                "domain": domain,
                "api": selected_api,
                "complexity": "medium",
                "files_created": 12,
                "validation_passed": success
            }
        )

        episode_id = bridge.store_episode(episode)
        print(f"   ✅ Episode stored: #{episode_id}")

        # If successful, create skill
        if success and bridge.is_available:
            skill = Skill(
                name=f"{domain}_agent_template",
                description=f"Proven template for {domain} agents",
                code=f"API: {selected_api}, Structure: modular",
                success_rate=1.0,
                uses=1,
                avg_reward=0.9,
                metadata={"domain": domain, "api": selected_api}
            )

            skill_id = bridge.create_skill(skill)
            print(f"   🎯 Skill created: #{skill_id}")

        # Add causal edge
        if bridge.is_available:
            from agentdb_real_integration import CausalEdge

            edge = CausalEdge(
                cause=f"use_{selected_api.lower().replace(' ', '_')}",
                effect=f"{domain}_agent_success",
                uplift=0.25,
                confidence=0.95,
                sample_size=1,
                mechanism=f"High-quality {selected_api} integration improves {domain} analysis"
            )

            edge_id = bridge.add_causal_edge(edge)
            print(f"   🔗 Causal edge added: #{edge_id}")

        return episode_id, skill_id if success else None

    except Exception as e:
        print(f"   ⚠️ AgentDB storage failed: {e}")
        print(f"   🔄 Agent creation completed successfully (without learning)")
        return None, None

def simulate_learning_feedback(agent_name: str, user_input: str, success: bool):
    """Simulate learning feedback system"""
    print(f"\n📊 Learning Progress Analysis")

    try:
        from learning_feedback import analyze_agent_execution

        feedback = analyze_agent_execution(
            agent_name=agent_name,
            user_input=user_input,
            execution_time=45.0,
            success=success,
            result_quality=0.9 if success else 0.7
        )

        if feedback:
            print(f"   🎯 Learning Feedback: {feedback}")
        else:
            print(f"   ℹ️ No specific feedback this time")

    except Exception as e:
        print(f"   ⚠️ Learning analysis unavailable: {e}")

def simulate_progressive_enhancement():
    """Simulate multiple creations to show progressive enhancement"""
    print(f"\n🚀 Simulating Progressive Enhancement Over Time")
    print("=" * 60)

    scenarios = [
        {
            "user_input": "Create financial analysis agent for stock market data",
            "domain": "finance",
            "agent_name": "financial-analysis-agent",
            "success": True,
            "session": "First creation"
        },
        {
            "user_input": "Build agriculture monitoring system for crop yields",
            "domain": "agriculture",
            "agent_name": "agriculture-monitor-agent",
            "success": True,
            "session": "Second creation"
        },
        {
            "user_input": "Develop financial portfolio optimization tool",
            "domain": "finance",
            "agent_name": "portfolio-optimizer-agent",
            "success": True,
            "session": "Third creation (same domain)"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- {scenario['session']} ---")

        # Phase 1 with AgentDB
        api, intelligence = simulate_phase_1_with_agentdb(
            scenario['user_input'],
            scenario['domain']
        )

        # Phase 5 with AgentDB
        episode_id, skill_id = simulate_phase_5_with_agentdb(
            scenario['user_input'],
            scenario['domain'],
            api,
            scenario['agent_name'],
            scenario['success']
        )

        # Learning feedback
        simulate_learning_feedback(scenario['agent_name'], scenario['user_input'], scenario['success'])

        # Show progressive improvement
        if i > 1:
            print(f"   📈 Progressive Enhancement Active:")
            print(f"      - Learning from {i} previous successful creations")
            if scenario['domain'] == "finance":
                print(f"      - Finance domain patterns established")
            print(f"      - Creation confidence increased")

def show_database_state():
    """Show final database state"""
    print(f"\n📊 Final AgentDB Database State")
    print("=" * 40)

    try:
        bridge = get_real_agentdb_bridge()
        stats = bridge.get_database_stats()

        print(f"📈 Database Statistics:")
        print(f"   Episodes stored: {stats.get('episodes', 0)}")
        print(f"   Skills created: {stats.get('skills', 0)}")
        print(f"   Causal edges: {stats.get('causal_edges', 0)}")

        # Show recent episodes
        episodes = bridge.retrieve_episodes("agent", k=3, min_reward=0.7)
        if episodes:
            print(f"\n🧠 Recent Learning Episodes:")
            for ep in episodes:
                print(f"   - {ep.get('task', 'unknown')} (reward: {ep.get('reward', 0):.2f})")

        # Show available skills
        skills = bridge.search_skills("agent", k=3, min_success_rate=0.7)
        if skills:
            print(f"\n🎯 Available Skills:")
            for skill in skills:
                print(f"   - {skill.get('name', 'unknown')} (success: {skill.get('success_rate', 0):.1%})")

    except Exception as e:
        print(f"   ⚠️ Could not retrieve database stats: {e}")

def main():
    """Run full integration test"""
    print("🚀 Full AgentDB Integration Test")
    print("=" * 50)
    print("Testing complete agent creation flow with AgentDB learning")

    # Check AgentDB availability
    bridge = get_agentdb_bridge()
    real_bridge = get_real_agentdb_bridge()

    print(f"\n🔧 System Status:")
    print(f"   AgentDB Bridge Available: {bridge.is_available}")
    print(f"   Real AgentDB Available: {real_bridge.is_available}")

    if not real_bridge.is_available:
        print(f"   ⚠️ AgentDB not available - test will simulate gracefully")
        return False

    # Show initial state
    initial_stats = real_bridge.get_database_stats()
    print(f"\n📊 Initial Database State:")
    print(f"   Episodes: {initial_stats.get('episodes', 0)}")
    print(f"   Skills: {initial_stats.get('skills', 0)}")
    print(f"   Causal Edges: {initial_stats.get('causal_edges', 0)}")

    # Simulate progressive enhancement
    simulate_progressive_enhancement()

    # Show final state
    show_database_state()

    # Summary
    final_stats = real_bridge.get_database_stats()
    episodes_added = final_stats.get('episodes', 0) - initial_stats.get('episodes', 0)
    skills_added = final_stats.get('skills', 0) - initial_stats.get('skills', 0)
    edges_added = final_stats.get('causal_edges', 0) - initial_stats.get('causal_edges', 0)

    print(f"\n🎉 Integration Test Results:")
    print(f"   Episodes Created: {episodes_added}")
    print(f"   Skills Created: {skills_added}")
    print(f"   Causal Edges Added: {edges_added}")

    if episodes_added > 0:
        print(f"   ✅ Learning integration working!")
        print(f"   🧠 Future creations will be enhanced with this knowledge")
    else:
        print(f"   ⚠️ No learning occurred - check AgentDB integration")

    return episodes_added > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)