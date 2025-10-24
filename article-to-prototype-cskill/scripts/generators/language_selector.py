"""
Language Selector

Selects the optimal programming language for prototype generation.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LanguageSelector:
    """Selects optimal language based on analysis"""

    # Domain to language mapping
    DOMAIN_LANGUAGE_MAP = {
        "machine_learning": "python",
        "data_science": "python",
        "web_development": "typescript",
        "systems_programming": "rust",
        "scientific_computing": "julia",
        "devops": "python",
        "general_programming": "python",
    }

    # Library to language mapping
    LIBRARY_TO_LANGUAGE = {
        # Python libraries
        "numpy": "python",
        "pandas": "python",
        "tensorflow": "python",
        "pytorch": "python",
        "sklearn": "python",
        "django": "python",
        "flask": "python",
        "requests": "python",
        # JavaScript libraries
        "react": "javascript",
        "vue": "javascript",
        "express": "javascript",
        "node": "javascript",
        "axios": "javascript",
        # Rust crates
        "tokio": "rust",
        "actix": "rust",
        "serde": "rust",
        # Go packages
        "gin": "go",
        "fiber": "go",
        # Java libraries
        "spring": "java",
        "junit": "java",
    }

    SUPPORTED_LANGUAGES = [
        "python", "javascript", "typescript", "rust", "go", "julia", "java", "cpp"
    ]

    def select_language(
        self,
        analysis: Any,
        hint: Optional[str] = None,
        default: str = "python"
    ) -> str:
        """
        Select optimal programming language.

        Args:
            analysis: AnalysisResult from ContentAnalyzer
            hint: Optional explicit language hint from user
            default: Default language if can't determine

        Returns:
            Selected language name
        """
        logger.info("Selecting programming language")

        # Priority 1: Explicit hint from user
        if hint and hint.lower() in self.SUPPORTED_LANGUAGES:
            logger.info(f"Using explicit hint: {hint}")
            return hint.lower()

        # Priority 2: Detect from code blocks
        detected = self._detect_from_code(analysis)
        if detected:
            logger.info(f"Detected from code: {detected}")
            return detected

        # Priority 3: Domain-based selection
        if analysis.domain in self.DOMAIN_LANGUAGE_MAP:
            candidate = self.DOMAIN_LANGUAGE_MAP[analysis.domain]
            logger.info(f"Selected from domain ({analysis.domain}): {candidate}")
            return candidate

        # Priority 4: Dependency-based selection
        dep_language = self._select_from_dependencies(analysis.dependencies)
        if dep_language:
            logger.info(f"Selected from dependencies: {dep_language}")
            return dep_language

        # Default
        logger.info(f"Using default language: {default}")
        return default

    def _detect_from_code(self, analysis: Any) -> Optional[str]:
        """Detect language from existing code blocks"""
        # Count language occurrences in code blocks
        language_counts: Dict[str, int] = {}

        # Check if analysis has code-related data
        if hasattr(analysis, 'metadata') and 'language_hints' in analysis.metadata:
            for hint in analysis.metadata['language_hints']:
                hint_lower = hint.lower()
                if hint_lower in self.SUPPORTED_LANGUAGES:
                    language_counts[hint_lower] = language_counts.get(hint_lower, 0) + 1

        # Return most common
        if language_counts:
            return max(language_counts, key=language_counts.get)

        return None

    def _select_from_dependencies(self, dependencies: List[Any]) -> Optional[str]:
        """Select language based on dependencies"""
        scores: Dict[str, int] = {lang: 0 for lang in self.SUPPORTED_LANGUAGES}

        for dep in dependencies:
            dep_name = dep.name.lower() if hasattr(dep, 'name') else str(dep).lower()

            if dep_name in self.LIBRARY_TO_LANGUAGE:
                lang = self.LIBRARY_TO_LANGUAGE[dep_name]
                scores[lang] += 1

        # Return language with highest score
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)

        return None

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()
