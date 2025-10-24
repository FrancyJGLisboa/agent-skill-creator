"""
Code Detector

Detects and analyzes code fragments, pseudocode, and language hints.
"""

import logging
import re
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CodeFragment:
    """Represents a detected code fragment"""
    content: str
    language: Optional[str]
    fragment_type: str  # 'code', 'pseudocode', 'snippet'
    line_number: int


@dataclass
class PseudocodeBlock:
    """Represents a pseudocode block"""
    content: str
    algorithm_name: str
    steps: List[str]


class CodeDetector:
    """Detects code and pseudocode in content"""

    PSEUDOCODE_INDICATORS = [
        'algorithm', 'procedure', 'begin', 'end', 'step', 'input:', 'output:'
    ]

    LANGUAGE_INDICATORS = {
        'python': ['def ', 'import ', 'print(', 'self.', '__init__'],
        'javascript': ['function', 'const ', 'let ', '=>', 'console.'],
        'java': ['public class', 'void ', 'System.out'],
        'c++': ['#include', 'cout', 'std::'],
        'rust': ['fn ', 'let mut', 'impl '],
        'go': ['func ', 'package ', ':='],
    }

    def detect_code_fragments(self, content: Any) -> List[CodeFragment]:
        """Detect all code and pseudocode fragments"""
        fragments = []

        # Code blocks from extractors
        for i, code_block in enumerate(content.code_blocks):
            fragment_type = 'pseudocode' if self._is_pseudocode(code_block.code) else 'code'

            fragments.append(CodeFragment(
                content=code_block.code,
                language=code_block.language,
                fragment_type=fragment_type,
                line_number=code_block.line_number or i
            ))

        logger.info(f"Detected {len(fragments)} code fragments")
        return fragments

    def detect_language_hints(self, content: Any) -> List[str]:
        """Detect mentioned programming languages"""
        hints = set()
        text_lower = content.raw_text.lower()

        # Explicit mentions
        for lang in self.LANGUAGE_INDICATORS.keys():
            if lang in text_lower or f'{lang} ' in text_lower:
                hints.add(lang)

        # From code block annotations
        for code_block in content.code_blocks:
            if code_block.language:
                hints.add(code_block.language)

        logger.debug(f"Detected language hints: {hints}")
        return list(hints)

    def extract_pseudocode(self, text: str) -> List[PseudocodeBlock]:
        """Extract and structure pseudocode blocks"""
        blocks = []

        # Simple pseudocode detection
        lines = text.split('\n')
        in_pseudocode = False
        current_block = []
        algo_name = ''

        for line in lines:
            line_lower = line.lower()

            # Check for algorithm start
            if any(ind in line_lower for ind in ['algorithm', 'procedure']):
                in_pseudocode = True
                algo_name = line.strip()
                current_block = []

            elif in_pseudocode:
                if line.strip() and not line.strip().startswith(('#', '//')):
                    current_block.append(line)

                # Check for end
                if 'end' in line_lower or (line.strip() == '' and len(current_block) > 3):
                    if current_block:
                        blocks.append(PseudocodeBlock(
                            content='\n'.join(current_block),
                            algorithm_name=algo_name,
                            steps=current_block
                        ))
                    in_pseudocode = False
                    current_block = []

        return blocks

    def _is_pseudocode(self, code: str) -> bool:
        """Check if code looks like pseudocode"""
        code_lower = code.lower()
        count = sum(1 for ind in self.PSEUDOCODE_INDICATORS if ind in code_lower)
        return count >= 2
