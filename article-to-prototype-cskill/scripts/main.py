"""
Article-to-Prototype Main Orchestrator

Coordinates the extraction, analysis, and generation pipeline.
"""

import logging
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

# Setup path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extractors.pdf_extractor import PDFExtractor, PDFExtractionError
from extractors.web_extractor import WebExtractor, WebExtractionError
from extractors.notebook_extractor import NotebookExtractor, NotebookExtractionError
from extractors.markdown_extractor import MarkdownExtractor, MarkdownExtractionError
from analyzers.content_analyzer import ContentAnalyzer
from analyzers.code_detector import CodeDetector
from generators.language_selector import LanguageSelector
from generators.prototype_generator import PrototypeGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArticleToPrototype:
    """Main orchestrator for article-to-prototype conversion"""

    def __init__(self):
        """Initialize orchestrator"""
        self.pdf_extractor = PDFExtractor()
        self.web_extractor = WebExtractor()
        self.notebook_extractor = NotebookExtractor()
        self.markdown_extractor = MarkdownExtractor()
        self.content_analyzer = ContentAnalyzer()
        self.code_detector = CodeDetector()
        self.language_selector = LanguageSelector()
        self.prototype_generator = PrototypeGenerator()

    def process(
        self,
        source: str,
        output_dir: str,
        language_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process article and generate prototype.

        Args:
            source: Path to file or URL
            output_dir: Output directory for generated prototype
            language_hint: Optional language hint from user

        Returns:
            Dictionary with generation results
        """
        logger.info(f"Processing source: {source}")

        try:
            # Step 1: Detect format and extract content
            logger.info("Step 1: Extracting content...")
            content = self._extract_content(source)

            # Step 2: Analyze content
            logger.info("Step 2: Analyzing content...")
            analysis = self.content_analyzer.analyze(content)
            code_fragments = self.code_detector.detect_code_fragments(content)
            language_hints = self.code_detector.detect_language_hints(content)

            # Add to analysis metadata
            analysis.metadata['code_fragments'] = len(code_fragments)
            analysis.metadata['language_hints'] = language_hints

            # Step 3: Select language
            logger.info("Step 3: Selecting programming language...")
            language = self.language_selector.select_language(
                analysis,
                hint=language_hint
            )

            # Step 4: Generate prototype
            logger.info(f"Step 4: Generating {language} prototype...")
            source_info = {
                'title': content.title,
                'source_url': content.source_url or source,
                'extraction_date': content.extraction_date.isoformat(),
            }

            result = self.prototype_generator.generate(
                analysis,
                language,
                output_dir,
                source_info
            )

            logger.info(f"✅ Successfully generated prototype in: {output_dir}")

            return {
                'success': True,
                'output_dir': output_dir,
                'language': language,
                'files_created': result.files_created,
                'entry_point': result.entry_point,
                'domain': analysis.domain,
                'complexity': analysis.complexity,
                'num_algorithms': len(analysis.algorithms),
                'confidence': analysis.confidence,
            }

        except Exception as e:
            logger.error(f"❌ Failed to process article: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
            }

    def _extract_content(self, source: str):
        """Extract content based on source type"""
        # Check if URL
        if source.startswith('http://') or source.startswith('https://'):
            logger.info(f"Detected web URL: {source}")
            return self.web_extractor.extract(source)

        # Check if file exists
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        # Detect file type
        ext = path.suffix.lower()

        if ext == '.pdf':
            logger.info("Detected PDF file")
            return self.pdf_extractor.extract(str(path))

        elif ext == '.ipynb':
            logger.info("Detected Jupyter notebook")
            return self.notebook_extractor.extract(str(path))

        elif ext in ['.md', '.markdown']:
            logger.info("Detected Markdown file")
            return self.markdown_extractor.extract(str(path))

        elif ext == '.txt':
            logger.info("Detected text file, treating as markdown")
            return self.markdown_extractor.extract(str(path))

        else:
            raise ValueError(f"Unsupported file type: {ext}")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Extract algorithms from articles and generate prototypes'
    )
    parser.add_argument(
        'source',
        help='Path to PDF, URL, notebook, or markdown file'
    )
    parser.add_argument(
        '-o', '--output',
        default='./output',
        help='Output directory (default: ./output)'
    )
    parser.add_argument(
        '-l', '--language',
        help='Target programming language (auto-detected if not specified)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Article-to-Prototype v1.0.0'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Process
    orchestrator = ArticleToPrototype()
    result = orchestrator.process(
        source=args.source,
        output_dir=args.output,
        language_hint=args.language
    )

    # Print results
    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"Generated {result['language']} prototype")
        print(f"Output directory: {result['output_dir']}")
        print(f"Entry point: {result['entry_point']}")
        print(f"Domain: {result['domain']}")
        print(f"Complexity: {result['complexity']}")
        print(f"Algorithms detected: {result['num_algorithms']}")
        print(f"Files created: {len(result['files_created'])}")
        print(f"\nTo run:")
        print(f"  cd {result['output_dir']}")
        print(f"  # Follow README.md instructions")
        return 0
    else:
        print(f"\n❌ FAILED: {result['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
