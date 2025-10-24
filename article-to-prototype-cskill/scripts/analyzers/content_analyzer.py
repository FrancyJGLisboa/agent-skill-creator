"""
Content Analyzer

Analyzes extracted content to identify technical concepts, algorithms,
architectures, and domain classification.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class Algorithm:
    """Represents a detected algorithm"""
    name: str
    description: str
    steps: List[str]
    complexity: Optional[str] = None
    pseudocode: Optional[str] = None


@dataclass
class Architecture:
    """Represents a detected architecture pattern"""
    name: str
    description: str
    components: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)


@dataclass
class Dependency:
    """Represents a dependency or required library"""
    name: str
    version: Optional[str] = None
    purpose: str = ''


@dataclass
class AnalysisResult:
    """Result of content analysis"""
    algorithms: List[Algorithm]
    architectures: List[Architecture]
    dependencies: List[Dependency]
    domain: str
    complexity: str  # "simple", "moderate", "complex"
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentAnalyzer:
    """Analyzes extracted content for technical concepts"""

    # Domain indicators with keywords
    DOMAIN_INDICATORS = {
        "machine_learning": [
            "neural network", "training", "model", "dataset", "accuracy",
            "loss function", "tensorflow", "pytorch", "keras", "scikit-learn",
            "classifier", "regression", "supervised", "unsupervised", "deep learning"
        ],
        "web_development": [
            "http", "rest", "api", "frontend", "backend", "server", "client",
            "route", "endpoint", "express", "react", "vue", "angular", "django",
            "flask", "authentication", "middleware"
        ],
        "systems_programming": [
            "concurrency", "thread", "process", "memory", "performance",
            "optimization", "low-level", "kernel", "system call", "scheduling",
            "mutex", "semaphore", "deadlock", "race condition"
        ],
        "data_science": [
            "pandas", "numpy", "analysis", "visualization", "statistics",
            "dataframe", "matplotlib", "seaborn", "jupyter", "correlation",
            "distribution", "hypothesis"
        ],
        "scientific_computing": [
            "numerical", "simulation", "computation", "algorithm", "matrix",
            "equation", "optimization", "julia", "fortran", "solver",
            "differential", "integration"
        ],
        "devops": [
            "docker", "kubernetes", "ci/cd", "deployment", "infrastructure",
            "container", "orchestration", "pipeline", "jenkins", "terraform",
            "monitoring", "logging"
        ]
    }

    # Algorithm keywords
    ALGORITHM_KEYWORDS = [
        "algorithm", "procedure", "method", "technique", "approach",
        "sort", "search", "traverse", "optimize", "compute", "calculate"
    ]

    # Architecture patterns
    ARCHITECTURE_PATTERNS = {
        "microservices": ["microservice", "service-oriented", "distributed services"],
        "mvc": ["model-view-controller", "mvc", "model view controller"],
        "layered": ["layered architecture", "n-tier", "three-tier", "multi-layer"],
        "event-driven": ["event-driven", "event bus", "event sourcing", "pub-sub"],
        "pipeline": ["pipeline", "data pipeline", "etl", "stream processing"],
        "client-server": ["client-server", "client/server", "server-client"],
    }

    # Library/dependency patterns
    LIBRARY_PATTERNS = [
        (re.compile(r'\b(?:import|from|require|include)\s+([a-zA-Z_][\w.]*)', re.IGNORECASE), 1),
        (re.compile(r'\b(?:using|with)\s+([a-zA-Z_][\w.]*)', re.IGNORECASE), 1),
        (re.compile(r'\bpip install\s+([a-zA-Z_][\w-]*)', re.IGNORECASE), 1),
        (re.compile(r'\bnpm install\s+([a-zA-Z_][\w-]*)', re.IGNORECASE), 1),
    ]

    def __init__(self):
        """Initialize content analyzer"""
        self.algorithm_pattern = re.compile(
            r'(?:algorithm|procedure|method)\s+(\d+)?[:\s]+(.+?)(?:\n|$)',
            re.IGNORECASE
        )
        self.complexity_pattern = re.compile(r'O\([^)]+\)', re.IGNORECASE)

    def analyze(self, content: Any) -> AnalysisResult:
        """
        Analyze extracted content for technical concepts.

        Args:
            content: ExtractedContent object from extractor

        Returns:
            AnalysisResult with detected algorithms, architectures, etc.
        """
        logger.info("Analyzing content")

        # Combine all text for analysis
        full_text = self._combine_text(content)

        # Detect algorithms
        algorithms = self.detect_algorithms(content)

        # Detect architectures
        architectures = self._detect_architectures(full_text)

        # Extract dependencies
        dependencies = self._extract_dependencies(content)

        # Classify domain
        domain = self.classify_domain(full_text)

        # Assess complexity
        complexity = self._assess_complexity(content)

        # Calculate confidence
        confidence = self._calculate_confidence(algorithms, architectures, domain)

        logger.info(f"Analysis complete: domain={domain}, complexity={complexity}, confidence={confidence:.2f}")

        return AnalysisResult(
            algorithms=algorithms,
            architectures=architectures,
            dependencies=dependencies,
            domain=domain,
            complexity=complexity,
            confidence=confidence,
            metadata={
                'num_algorithms': len(algorithms),
                'num_architectures': len(architectures),
                'num_dependencies': len(dependencies),
            }
        )

    def _combine_text(self, content: Any) -> str:
        """Combine all text content for analysis"""
        parts = [content.raw_text]

        # Add section content
        for section in content.sections:
            parts.append(section.heading)
            parts.append(section.content)

        # Add code context
        for code_block in content.code_blocks:
            if code_block.context:
                parts.append(code_block.context)

        return '\n'.join(parts).lower()

    def detect_algorithms(self, content: Any) -> List[Algorithm]:
        """Detect and extract algorithms from content"""
        algorithms = []

        # Search in raw text
        text = content.raw_text

        # Method 1: Look for explicit algorithm declarations
        for match in self.algorithm_pattern.finditer(text):
            algo_num = match.group(1)
            algo_desc = match.group(2).strip()

            # Extract steps (look for numbered lists after the declaration)
            steps = self._extract_algorithm_steps(text, match.end())

            # Try to find complexity
            complexity = None
            complexity_match = self.complexity_pattern.search(text[match.start():match.end() + 500])
            if complexity_match:
                complexity = complexity_match.group(0)

            algorithms.append(Algorithm(
                name=f"Algorithm {algo_num}" if algo_num else "Algorithm",
                description=algo_desc,
                steps=steps,
                complexity=complexity
            ))

        # Method 2: Look in code blocks for algorithmic code
        for code_block in content.code_blocks:
            if self._is_algorithmic_code(code_block.code):
                algorithms.append(Algorithm(
                    name=code_block.context[:50] if code_block.context else "Detected Algorithm",
                    description=code_block.context or "Algorithm from code",
                    steps=[],
                    pseudocode=code_block.code
                ))

        logger.debug(f"Detected {len(algorithms)} algorithms")
        return algorithms

    def _extract_algorithm_steps(self, text: str, start_pos: int) -> List[str]:
        """Extract numbered steps following an algorithm declaration"""
        steps = []
        lines = text[start_pos:start_pos + 1000].split('\n')

        step_pattern = re.compile(r'^\s*(?:\d+[\.\)]\s+|[-*]\s+)(.+)$')

        for line in lines:
            match = step_pattern.match(line)
            if match:
                steps.append(match.group(1).strip())
            elif steps and line.strip() == '':
                # Empty line might indicate end of steps
                break
            elif steps:
                # Non-step line after steps started, might be end
                if not line.strip():
                    continue
                if line[0].isalpha() and not line.strip().startswith('-'):
                    break

        return steps[:20]  # Max 20 steps

    def _is_algorithmic_code(self, code: str) -> bool:
        """Check if code looks like an algorithm implementation"""
        code_lower = code.lower()

        # Look for algorithmic patterns
        patterns = [
            'def ', 'function ', 'procedure',
            'for ', 'while ', 'loop',
            'if ', 'else', 'switch', 'case',
            'return', 'yield'
        ]

        count = sum(1 for pattern in patterns if pattern in code_lower)
        return count >= 3  # At least 3 algorithmic keywords

    def _detect_architectures(self, text: str) -> List[Architecture]:
        """Detect architecture patterns"""
        architectures = []

        for arch_name, keywords in self.ARCHITECTURE_PATTERNS.items():
            for keyword in keywords:
                if keyword in text:
                    # Found architecture mention
                    context = self._extract_context(text, keyword, 200)

                    architectures.append(Architecture(
                        name=arch_name.replace('_', ' ').title(),
                        description=context,
                        components=[],
                        relationships=[]
                    ))
                    break  # Don't duplicate

        logger.debug(f"Detected {len(architectures)} architectures")
        return architectures

    def _extract_context(self, text: str, keyword: str, window: int = 200) -> str:
        """Extract context around a keyword"""
        pos = text.index(keyword)
        start = max(0, pos - window // 2)
        end = min(len(text), pos + len(keyword) + window // 2)
        return text[start:end].strip()

    def _extract_dependencies(self, content: Any) -> List[Dependency]:
        """Extract dependencies from code and text"""
        dependencies = {}

        # Extract from code blocks
        for code_block in content.code_blocks:
            for pattern, group_num in self.LIBRARY_PATTERNS:
                matches = pattern.findall(code_block.code)
                for match in matches:
                    lib_name = match.split('.')[0].strip()
                    if lib_name and len(lib_name) > 1:
                        dependencies[lib_name] = Dependency(
                            name=lib_name,
                            version=None,
                            purpose='Detected from imports'
                        )

        # Extract from notebook metadata if available
        if 'dependencies' in content.metadata:
            for dep in content.metadata['dependencies']:
                if dep not in dependencies:
                    dependencies[dep] = Dependency(
                        name=dep,
                        version=None,
                        purpose='Detected from notebook'
                    )

        logger.debug(f"Extracted {len(dependencies)} dependencies")
        return list(dependencies.values())

    def classify_domain(self, text: str) -> str:
        """
        Classify content domain based on keywords.

        Args:
            text: Text content (should be lowercase)

        Returns:
            Domain name
        """
        scores = {domain: 0 for domain in self.DOMAIN_INDICATORS}

        # Count keyword occurrences
        for domain, keywords in self.DOMAIN_INDICATORS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[domain] += 1

        # Find highest scoring domain
        if max(scores.values()) > 0:
            domain = max(scores, key=scores.get)
            logger.debug(f"Classified as {domain} (score: {scores[domain]})")
            return domain

        # Default to general programming
        return "general_programming"

    def _assess_complexity(self, content: Any) -> str:
        """Assess content complexity"""
        # Simple heuristics
        score = 0

        # More sections = more complex
        if len(content.sections) > 10:
            score += 2
        elif len(content.sections) > 5:
            score += 1

        # More code blocks = more complex
        if len(content.code_blocks) > 5:
            score += 2
        elif len(content.code_blocks) > 2:
            score += 1

        # Long content = more complex
        if len(content.raw_text) > 10000:
            score += 2
        elif len(content.raw_text) > 5000:
            score += 1

        # Technical terms indicate complexity
        technical_terms = [
            'algorithm', 'optimization', 'complexity', 'architecture',
            'distributed', 'concurrent', 'asynchronous'
        ]
        text_lower = content.raw_text.lower()
        score += sum(1 for term in technical_terms if term in text_lower)

        # Classify
        if score >= 6:
            return "complex"
        elif score >= 3:
            return "moderate"
        else:
            return "simple"

    def _calculate_confidence(
        self,
        algorithms: List[Algorithm],
        architectures: List[Architecture],
        domain: str
    ) -> float:
        """Calculate confidence score for analysis"""
        confidence = 0.5  # Base confidence

        # More detected concepts = higher confidence
        if algorithms:
            confidence += 0.2
        if architectures:
            confidence += 0.1

        # Non-default domain = higher confidence
        if domain != "general_programming":
            confidence += 0.2

        return min(1.0, confidence)
