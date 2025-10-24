#!/usr/bin/env python3
"""
AgentDB Bridge - Invisible Intelligence Layer

This module provides seamless AgentDB integration that is completely transparent
to the end user. All complexity is hidden behind simple interfaces.

The user never needs to know AgentDB exists - they just get smarter agents.

Principles:
- Zero configuration required
- Automatic setup and maintenance
- Graceful fallback if AgentDB unavailable
- Progressive enhancement without user awareness
"""

import json
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentDBIntelligence:
    """Container for AgentDB-enhanced decision making"""
    template_choice: Optional[str] = None
    success_probability: float = 0.0
    learned_improvements: List[str] = None
    historical_context: Dict[str, Any] = None
    mathematical_proof: Optional[str] = None

    def __post_init__(self):
        if self.learned_improvements is None:
            self.learned_improvements = []
        if self.historical_context is None:
            self.historical_context = {}

class AgentDBBridge:
    """
    Invisible AgentDB integration layer.

    Provides AgentDB capabilities without exposing complexity to users.
    All AgentDB operations happen transparently behind the scenes.
    """

    def __init__(self):
        self.is_available = False
        self.is_configured = False
        self.error_count = 0
        self.max_errors = 3  # Graceful fallback after 3 errors

        # Initialize silently
        self._initialize_silently()

    def _initialize_silently(self):
        """Initialize AgentDB silently without user intervention"""
        try:
            # Step 1: Try detection first (current behavior)
            cli_available = self._check_cli_availability()
            npx_available = self._check_npx_availability()

            if cli_available or npx_available:
                self.is_available = True
                self.use_cli = cli_available  # Prefer native CLI
                self._auto_configure()
                logger.info("AgentDB initialized successfully (invisible mode)")
                return

            # Step 2: Try automatic installation if not found
            logger.info("AgentDB not found - attempting automatic installation")
            if self._attempt_automatic_install():
                logger.info("AgentDB automatically installed and configured")
                return

            # Step 3: Fallback mode if installation fails
            logger.info("AgentDB not available - using fallback mode")

        except Exception as e:
            logger.info(f"AgentDB initialization failed: {e} - using fallback mode")

    def _check_cli_availability(self) -> bool:
        """Check if AgentDB native CLI is available"""
        try:
            result = subprocess.run(
                ["agentdb", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_npx_availability(self) -> bool:
        """Check if AgentDB is available via npx"""
        try:
            result = subprocess.run(
                ["npx", "@anthropic-ai/agentdb", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _attempt_automatic_install(self) -> bool:
        """Attempt to install AgentDB automatically"""
        try:
            # Check if npm is available first
            if not self._check_npm_availability():
                logger.info("npm not available - cannot install AgentDB automatically")
                return False

            # Try installation methods in order of preference
            installation_methods = [
                self._install_npm_global,
                self._install_npx_fallback
            ]

            for method in installation_methods:
                try:
                    if method():
                        # Verify installation worked
                        if self._verify_installation():
                            self.is_available = True
                            self._auto_configure()
                            logger.info("AgentDB automatically installed and configured")
                            return True
                except Exception as e:
                    logger.info(f"Installation method failed: {e}")
                    continue

            logger.info("All automatic installation methods failed")
            return False

        except Exception as e:
            logger.info(f"Automatic installation failed: {e}")
            return False

    def _check_npm_availability(self) -> bool:
        """Check if npm is available"""
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _install_npm_global(self) -> bool:
        """Install AgentDB globally via npm"""
        try:
            logger.info("Attempting npm global installation of AgentDB...")
            result = subprocess.run(
                ["npm", "install", "-g", "@anthropic-ai/agentdb"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                logger.info("npm global installation successful")
                return True
            else:
                logger.info(f"npm global installation failed: {result.stderr}")
                return False

        except Exception as e:
            logger.info(f"npm global installation error: {e}")
            return False

    def _install_npx_fallback(self) -> bool:
        """Try to use npx approach (doesn't require global installation)"""
        try:
            logger.info("Testing npx approach for AgentDB...")
            # Test if npx can download and run agentdb
            result = subprocess.run(
                ["npx", "@anthropic-ai/agentdb", "--version"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info("npx approach successful - AgentDB available via npx")
                return True
            else:
                logger.info(f"npx approach failed: {result.stderr}")
                return False

        except Exception as e:
            logger.info(f"npx approach error: {e}")
            return False

    def _verify_installation(self) -> bool:
        """Verify that AgentDB was installed successfully"""
        try:
            # Check CLI availability first
            if self._check_cli_availability():
                logger.info("AgentDB CLI verified after installation")
                return True

            # Check npx availability as fallback
            if self._check_npx_availability():
                logger.info("AgentDB npx availability verified after installation")
                return True

            logger.info("AgentDB installation verification failed")
            return False

        except Exception as e:
            logger.info(f"Installation verification error: {e}")
            return False

    def _auto_configure(self):
        """Auto-configure AgentDB for optimal performance"""
        try:
            # Create default configuration
            config = {
                "reflexion": {
                    "auto_save": True,
                    "compression": True
                },
                "causal": {
                    "auto_track": True,
                    "utility_model": "outcome_based"
                },
                "skills": {
                    "auto_extract": True,
                    "success_threshold": 0.8
                },
                "nightly_learner": {
                    "enabled": True,
                    "schedule": "2:00 AM"
                }
            }

            # Write configuration silently
            config_path = Path.home() / ".agentdb" / "config.json"
            config_path.parent.mkdir(exist_ok=True)

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            self.is_configured = True
            logger.info("AgentDB auto-configured successfully")

        except Exception as e:
            logger.warning(f"AgentDB auto-configuration failed: {e}")

    def enhance_agent_creation(self, user_input: str, domain: str = None) -> AgentDBIntelligence:
        """
        Enhance agent creation with AgentDB intelligence.
        Returns intelligence data transparently.
        """
        intelligence = AgentDBIntelligence()

        if not self.is_available or not self.is_configured:
            return intelligence  # Return empty intelligence for fallback

        try:
            # Use real AgentDB commands if CLI is available
            if hasattr(self, 'use_cli') and self.use_cli:
                intelligence = self._enhance_with_real_agentdb(user_input, domain)
            else:
                # Fallback to legacy implementation
                intelligence = self._enhance_with_legacy_agentdb(user_input, domain)

            # Store this decision for learning
            self._store_creation_decision(user_input, intelligence)

            logger.info(f"AgentDB enhanced creation: template={intelligence.template_choice}")

        except Exception as e:
            logger.warning(f"AgentDB enhancement failed: {e}")
            # Return empty intelligence on error
            self.error_count += 1
            if self.error_count >= self.max_errors:
                logger.warning("AgentDB error threshold reached, switching to fallback mode")
                self.is_available = False

        return intelligence

    def _enhance_with_real_agentdb(self, user_input: str, domain: str = None) -> AgentDBIntelligence:
        """Enhance using real AgentDB CLI commands"""
        intelligence = AgentDBIntelligence()

        try:
            # 1. Search for relevant skills
            skills_result = self._execute_agentdb_command([
                "agentdb" if self.use_cli else "npx", "agentdb", "skill", "search", user_input, "5"
            ])

            if skills_result:
                # Parse skills from output
                skills = self._parse_skills_from_output(skills_result)
                if skills:
                    intelligence.learned_improvements = [f"Skill available: {skill.get('name', 'unknown')}" for skill in skills[:3]]

            # 2. Retrieve relevant episodes
            episodes_result = self._execute_agentdb_command([
                "agentdb" if self.use_cli else "npx", "agentdb", "reflexion", "retrieve", user_input, "3", "0.6"
            ])

            if episodes_result:
                episodes = self._parse_episodes_from_output(episodes_result)
                if episodes:
                    success_rate = sum(1 for e in episodes if e.get('success', False)) / len(episodes)
                    intelligence.success_probability = success_rate

            # 3. Query causal effects
            if domain:
                causal_result = self._execute_agentdb_command([
                    "agentdb" if self.use_cli else "npx", "agentdb", "causal", "query",
                    f"use_{domain}_template", "", "0.7", "0.1", "5"
                ])

                if causal_result:
                    # Parse best causal effect
                    effects = self._parse_causal_effects_from_output(causal_result)
                    if effects:
                        best_effect = max(effects, key=lambda x: x.get('uplift', 0))
                        intelligence.template_choice = f"{domain}-analysis"
                        intelligence.mathematical_proof = f"Causal uplift: {best_effect.get('uplift', 0):.2%}"

            logger.info(f"Real AgentDB enhancement completed for {domain}")

        except Exception as e:
            logger.error(f"Real AgentDB enhancement failed: {e}")

        return intelligence

    def _enhance_with_legacy_agentdb(self, user_input: str, domain: str = None) -> AgentDBIntelligence:
        """Enhance using legacy AgentDB implementation"""
        intelligence = AgentDBIntelligence()

        try:
            # Legacy implementation using npx
            template_result = self._execute_agentdb_command([
                "npx", "agentdb", "causal", "recall",
                f"best_template_for_domain:{domain or 'unknown'}",
                "--format", "json"
            ])

            if template_result:
                intelligence.template_choice = self._parse_template_result(template_result)
                intelligence.success_probability = self._calculate_success_probability(
                    intelligence.template_choice, domain
                )

            # Get learned improvements
            improvements_result = self._execute_agentdb_command([
                "npx", "agentdb", "skills", "list",
                f"domain:{domain or 'unknown'}",
                "--success-rate", "0.8"
            ])

            if improvements_result:
                intelligence.learned_improvements = self._parse_improvements(improvements_result)

            logger.info(f"Legacy AgentDB enhancement completed for {domain}")

        except Exception as e:
            logger.error(f"Legacy AgentDB enhancement failed: {e}")

        return intelligence

    def _parse_skills_from_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse skills from AgentDB CLI output"""
        skills = []
        lines = output.split('\n')
        current_skill = {}

        for line in lines:
            line = line.strip()
            if line.startswith("#") and "Found" not in line:
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

        if current_skill:
            skills.append(current_skill)

        return skills

    def _parse_episodes_from_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse episodes from AgentDB CLI output"""
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
                elif key == "Success":
                    current_episode["success"] = "Yes" in value
                elif key == "Reward":
                    try:
                        current_episode["reward"] = float(value)
                    except ValueError:
                        pass

        if current_episode:
            episodes.append(current_episode)

        return episodes

    def _parse_causal_effects_from_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse causal effects from AgentDB CLI output"""
        effects = []
        lines = output.split('\n')

        for line in lines:
            if "→" in line and "uplift" in line.lower():
                parts = line.split("→")
                if len(parts) >= 2:
                    cause = parts[0].strip()
                    effect_rest = parts[1]
                    effect = effect_rest.split("(")[0].strip()

                    uplift = 0.0
                    if "uplift:" in effect_rest:
                        uplift_part = effect_rest.split("uplift:")[1].split(",")[0].strip()
                        try:
                            uplift = float(uplift_part)
                        except ValueError:
                            pass

                    effects.append({
                        "cause": cause,
                        "effect": effect,
                        "uplift": uplift
                    })

        return effects

    def _execute_agentdb_command(self, command: List[str]) -> Optional[str]:
        """Execute AgentDB command and return output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(Path.cwd())
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.debug(f"AgentDB command failed: {result.stderr}")
                return None

        except Exception as e:
            logger.debug(f"AgentDB command execution failed: {e}")
            return None

    def _parse_template_result(self, result: str) -> Optional[str]:
        """Parse template selection result"""
        try:
            if result.strip().startswith('{'):
                data = json.loads(result)
                return data.get('template', 'default')
            else:
                return result.strip()
        except:
            return None

    def _parse_improvements(self, result: str) -> List[str]:
        """Parse learned improvements result"""
        try:
            if result.strip().startswith('{'):
                data = json.loads(result)
                return data.get('improvements', [])
            else:
                return [line.strip() for line in result.split('\n') if line.strip()]
        except:
            return []

    def _calculate_success_probability(self, template: str, domain: str) -> float:
        """Calculate success probability based on historical data"""
        # Simplified calculation - in real implementation this would query AgentDB
        base_prob = 0.8  # Base success rate

        # Increase probability for templates with good history
        if template and "financial" in template.lower():
            base_prob += 0.1
        if template and "analysis" in template.lower():
            base_prob += 0.05

        return min(base_prob, 0.95)  # Cap at 95%

    def _store_creation_decision(self, user_input: str, intelligence: AgentDBIntelligence):
        """Store creation decision for learning"""
        if not self.is_available:
            return

        try:
            # Create session ID
            session_id = f"creation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            # Store reflexion data
            self._execute_agentdb_command([
                "npx", "agentdb", "reflexion", "store",
                session_id,
                "agent_creation_decision",
                str(intelligence.success_probability * 100)
            ])

            # Store causal relationship
            if intelligence.template_choice:
                self._execute_agentdb_command([
                    "npx", "agentdb", "causal", "store",
                    f"user_input:{user_input[:50]}...",
                    f"template_selected:{intelligence.template_choice}",
                    "created_successfully"
                ])

            logger.info(f"Stored creation decision: {session_id}")

        except Exception as e:
            logger.debug(f"Failed to store creation decision: {e}")

    def enhance_template(self, template_name: str, domain: str) -> Dict[str, Any]:
        """
        Enhance template with learned improvements
        """
        enhancements = {
            "agentdb_integration": {
                "enabled": self.is_available,
                "success_rate": 0.0,
                "learned_improvements": [],
                "historical_usage": 0
            }
        }

        if not self.is_available:
            return enhancements

        try:
            # Get historical success rate
            success_result = self._execute_agentdb_command([
                "npx", "agentdb", "causal", "recall",
                f"template_success_rate:{template_name}"
            ])

            if success_result:
                try:
                    success_data = json.loads(success_result)
                    enhancements["agentdb_integration"]["success_rate"] = success_data.get("success_rate", 0.8)
                    enhancements["agentdb_integration"]["historical_usage"] = success_data.get("usage_count", 0)
                except:
                    enhancements["agentdb_integration"]["success_rate"] = 0.8

            # Get learned improvements
            improvements_result = self._execute_agentdb_command([
                "npx", "agentdb", "skills", "list",
                f"template:{template_name}"
            ])

            if improvements_result:
                enhancements["agentdb_integration"]["learned_improvements"] = self._parse_improvements(improvements_result)

            logger.info(f"Template {template_name} enhanced with AgentDB intelligence")

        except Exception as e:
            logger.debug(f"Failed to enhance template {template_name}: {e}")

        return enhancements

    def store_agent_experience(self, agent_name: str, experience: Dict[str, Any]):
        """
        Store agent experience for learning
        """
        if not self.is_available:
            return

        try:
            session_id = f"agent-{agent_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            # Store reflexion
            success_rate = experience.get('success_rate', 0.5)
            self._execute_agentdb_command([
                "npx", "agentdb", "reflexion", "store",
                session_id,
                "agent_execution",
                str(int(success_rate * 100))
            ])

            # Store causal relationships
            for cause, effect in experience.get('causal_observations', {}).items():
                self._execute_agentdb_command([
                    "npx", "agentdb", "causal", "store",
                    str(cause),
                    str(effect),
                    "agent_observation"
                ])

            # Extract skills if successful
            if success_rate > 0.8:
                for skill_data in experience.get('successful_skills', []):
                    self._execute_agentdb_command([
                        "npx", "agentdb", "skills", "store",
                        skill_data.get('name', 'unnamed_skill'),
                        json.dumps(skill_data)
                    ])

            logger.info(f"Stored experience for agent: {agent_name}")

        except Exception as e:
            logger.debug(f"Failed to store agent experience: {e}")

    def get_learning_summary(self, agent_name: str) -> Dict[str, Any]:
        """
        Get learning summary for an agent (for internal use)
        """
        summary = {
            "total_sessions": 0,
            "success_rate": 0.0,
            "learned_skills": [],
            "causal_patterns": []
        }

        if not self.is_available:
            return summary

        try:
            # Get reflexion history
            reflexion_result = self._execute_agentdb_command([
                "npx", "agentdb", "reflexion", "recall",
                f"agent:{agent_name}",
                "--format", "json"
            ])

            if reflexion_result:
                try:
                    data = json.loads(reflexion_result)
                    summary["total_sessions"] = len(data.get('sessions', []))

                    if data.get('sessions'):
                        rewards = [s.get('reward', 0) for s in data['sessions']]
                        summary["success_rate"] = sum(rewards) / len(rewards) / 100
                except:
                    pass

            # Get learned skills
            skills_result = self._execute_agentdb_command([
                "npx", "agentdb", "skills", "list",
                f"agent:{agent_name}"
            ])

            if skills_result:
                summary["learned_skills"] = self._parse_improvements(skills_result)

            # Get causal patterns
            causal_result = self._execute_agentdb_command([
                "npx", "agentdb", "causal", "recall",
                f"agent:{agent_name}",
                "--format", "json"
            ])

            if causal_result:
                try:
                    data = json.loads(causal_result)
                    summary["causal_patterns"] = data.get('patterns', [])
                except:
                    pass

        except Exception as e:
            logger.debug(f"Failed to get learning summary for {agent_name}: {e}")

        return summary

# Global instance - invisible to users
_agentdb_bridge = None

def get_agentdb_bridge() -> AgentDBBridge:
    """Get the global AgentDB bridge instance"""
    global _agentdb_bridge
    if _agentdb_bridge is None:
        _agentdb_bridge = AgentDBBridge()
    return _agentdb_bridge

def enhance_agent_creation(user_input: str, domain: str = None) -> AgentDBIntelligence:
    """
    Public interface for enhancing agent creation with AgentDB intelligence.
    This is what the Agent-Creator calls internally.

    The user never calls this directly - it's all hidden behind the scenes.
    """
    bridge = get_agentdb_bridge()
    return bridge.enhance_agent_creation(user_input, domain)

def enhance_template(template_name: str, domain: str) -> Dict[str, Any]:
    """
    Enhance a template with AgentDB learned improvements.
    Called internally during template selection.
    """
    bridge = get_agentdb_bridge()
    return bridge.enhance_template(template_name, domain)

def store_agent_experience(agent_name: str, experience: Dict[str, Any]):
    """
    Store agent execution experience for learning.
    Called internally after agent execution.
    """
    bridge = get_agentdb_bridge()
    bridge.store_agent_experience(agent_name, experience)

def get_agent_learning_summary(agent_name: str) -> Dict[str, Any]:
    """
    Get learning summary for an agent.
    Used internally for progress tracking.
    """
    bridge = get_agentdb_bridge()
    return bridge.get_learning_summary(agent_name)

# Auto-initialize when module is imported
get_agentdb_bridge()