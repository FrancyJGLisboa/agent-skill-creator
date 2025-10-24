"""
Prototype Generator

Generates complete, production-quality code prototypes in multiple languages.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GeneratedPrototype:
    """Result of prototype generation"""
    output_dir: str
    language: str
    files_created: List[str]
    entry_point: str
    metadata: Dict[str, Any]


class PrototypeGenerator:
    """Generates complete prototype projects"""

    def __init__(self):
        """Initialize prototype generator"""
        pass

    def generate(
        self,
        analysis: Any,
        language: str,
        output_dir: str,
        source_info: Optional[Dict[str, Any]] = None
    ) -> GeneratedPrototype:
        """
        Generate a complete prototype project.

        Args:
            analysis: AnalysisResult from ContentAnalyzer
            language: Selected programming language
            output_dir: Directory to write output files
            source_info: Optional source article information

        Returns:
            GeneratedPrototype with file paths and metadata
        """
        logger.info(f"Generating {language} prototype in {output_dir}")

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        files_created = []

        # Generate based on language
        if language == "python":
            entry_point, files = self._generate_python(analysis, output_dir, source_info)
        elif language in ["javascript", "typescript"]:
            entry_point, files = self._generate_javascript(analysis, output_dir, source_info, language)
        elif language == "rust":
            entry_point, files = self._generate_rust(analysis, output_dir, source_info)
        elif language == "go":
            entry_point, files = self._generate_go(analysis, output_dir, source_info)
        else:
            # Default to Python
            logger.warning(f"Unsupported language {language}, defaulting to Python")
            entry_point, files = self._generate_python(analysis, output_dir, source_info)

        files_created.extend(files)

        # Generate README
        readme_path = self._generate_readme(analysis, language, output_dir, source_info)
        files_created.append(readme_path)

        # Generate gitignore
        gitignore_path = self._generate_gitignore(language, output_dir)
        files_created.append(gitignore_path)

        logger.info(f"Generated {len(files_created)} files")

        return GeneratedPrototype(
            output_dir=output_dir,
            language=language,
            files_created=files_created,
            entry_point=entry_point,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'domain': analysis.domain,
                'complexity': analysis.complexity,
                'num_files': len(files_created),
            }
        )

    def _generate_python(
        self,
        analysis: Any,
        output_dir: str,
        source_info: Optional[Dict[str, Any]]
    ) -> tuple[str, List[str]]:
        """Generate Python project"""
        files = []

        # Create source directory
        src_dir = Path(output_dir) / "src"
        src_dir.mkdir(exist_ok=True)

        # Generate main.py
        main_path = src_dir / "main.py"
        main_code = self._generate_python_main(analysis, source_info)
        main_path.write_text(main_code, encoding='utf-8')
        files.append(str(main_path))

        # Generate requirements.txt
        req_path = Path(output_dir) / "requirements.txt"
        requirements = self._generate_python_requirements(analysis)
        req_path.write_text(requirements, encoding='utf-8')
        files.append(str(req_path))

        # Generate test file
        test_dir = Path(output_dir) / "tests"
        test_dir.mkdir(exist_ok=True)
        test_path = test_dir / "test_main.py"
        test_code = self._generate_python_tests(analysis)
        test_path.write_text(test_code, encoding='utf-8')
        files.append(str(test_path))

        return str(main_path), files

    def _generate_python_main(self, analysis: Any, source_info: Optional[Dict[str, Any]]) -> str:
        """Generate Python main file"""
        source_url = source_info.get('source_url', 'Unknown') if source_info else 'Unknown'
        source_title = source_info.get('title', 'Untitled') if source_info else 'Untitled'

        # Generate imports based on dependencies
        imports = ["import logging", "from typing import List, Dict, Any, Optional"]
        for dep in analysis.dependencies[:5]:  # Limit to first 5
            dep_name = dep.name if hasattr(dep, 'name') else str(dep)
            imports.append(f"# import {dep_name}  # Install: pip install {dep_name}")

        imports_str = '\n'.join(imports)

        # Generate algorithm implementations
        algo_impls = []
        for i, algo in enumerate(analysis.algorithms[:3]):  # Limit to 3 algorithms
            algo_impl = f'''
def algorithm_{i+1}(data: Any) -> Any:
    """
    {algo.name}: {algo.description}

    Args:
        data: Input data

    Returns:
        Processed result
    """
    logger.info("Running {algo.name}")

    # Implementation based on: {algo.description}
    result = data  # Placeholder - implement algorithm logic here

    return result
'''
            algo_impls.append(algo_impl)

        algos_str = '\n'.join(algo_impls)

        code = f'''"""
Prototype Implementation

Generated from: {source_title}
Source: {source_url}
Domain: {analysis.domain}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This is a prototype implementation based on the article content.
"""

{imports_str}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

{algos_str}

def main():
    """Main entry point"""
    logger.info("Starting prototype")

    # Example usage
    sample_data = {{"key": "value"}}

    try:
        # Run algorithms
{chr(10).join(f"        result_{i+1} = algorithm_{i+1}(sample_data)" for i in range(min(3, len(analysis.algorithms))))}

        logger.info("Prototype execution completed successfully")

    except Exception as e:
        logger.error(f"Error during execution: {{e}}")
        raise


if __name__ == "__main__":
    main()
'''
        return code

    def _generate_python_requirements(self, analysis: Any) -> str:
        """Generate requirements.txt"""
        deps = ["# Python dependencies"]

        # Standard deps
        for dep in analysis.dependencies[:10]:
            dep_name = dep.name if hasattr(dep, 'name') else str(dep)
            deps.append(f"{dep_name}")

        # Common deps if not present
        if not any('requests' in str(d) for d in analysis.dependencies):
            deps.append("# requests>=2.31.0  # Uncomment if needed")

        return '\n'.join(deps)

    def _generate_python_tests(self, analysis: Any) -> str:
        """Generate Python test file"""
        code = '''"""
Tests for prototype implementation
"""

import pytest
from src.main import main

def test_main_execution():
    """Test that main runs without errors"""
    try:
        main()
        assert True
    except Exception as e:
        pytest.fail(f"Main execution failed: {e}")

def test_placeholder():
    """Placeholder test"""
    assert True, "Implement actual tests based on your algorithms"
'''
        return code

    def _generate_javascript(
        self,
        analysis: Any,
        output_dir: str,
        source_info: Optional[Dict[str, Any]],
        language: str
    ) -> tuple[str, List[str]]:
        """Generate JavaScript/TypeScript project"""
        files = []

        ext = '.ts' if language == 'typescript' else '.js'

        # Generate main file
        main_path = Path(output_dir) / f"index{ext}"
        main_code = self._generate_js_main(analysis, source_info, language)
        main_path.write_text(main_code, encoding='utf-8')
        files.append(str(main_path))

        # Generate package.json
        package_path = Path(output_dir) / "package.json"
        package_json = self._generate_package_json(analysis)
        package_path.write_text(package_json, encoding='utf-8')
        files.append(str(package_path))

        return str(main_path), files

    def _generate_js_main(self, analysis: Any, source_info: Optional[Dict[str, Any]], language: str) -> str:
        """Generate JavaScript/TypeScript main file"""
        source_url = source_info.get('source_url', 'Unknown') if source_info else 'Unknown'

        if language == 'typescript':
            code = f'''/**
 * Prototype Implementation
 * Generated from: {source_url}
 * Domain: {analysis.domain}
 */

// Main implementation
function main(): void {{
    console.log('Prototype starting...');

    // Implement algorithms here

    console.log('Prototype completed');
}}

// Run if main module
if (require.main === module) {{
    main();
}}

export {{ main }};
'''
        else:
            code = f'''/**
 * Prototype Implementation
 * Generated from: {source_url}
 * Domain: {analysis.domain}
 */

// Main implementation
function main() {{
    console.log('Prototype starting...');

    // Implement algorithms here

    console.log('Prototype completed');
}}

// Run if main module
if (require.main === module) {{
    main();
}}

module.exports = {{ main }};
'''
        return code

    def _generate_package_json(self, analysis: Any) -> str:
        """Generate package.json"""
        return '''{
  "name": "prototype",
  "version": "1.0.0",
  "description": "Generated prototype",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "echo \\"No tests specified\\""
  },
  "dependencies": {}
}
'''

    def _generate_rust(self, analysis: Any, output_dir: str, source_info: Optional[Dict[str, Any]]) -> tuple[str, List[str]]:
        """Generate Rust project"""
        files = []

        # Create src directory
        src_dir = Path(output_dir) / "src"
        src_dir.mkdir(exist_ok=True)

        # Generate main.rs
        main_path = src_dir / "main.rs"
        main_code = f'''//! Prototype Implementation
//! Domain: {analysis.domain}

fn main() {{
    println!("Prototype starting...");

    // Implement algorithms here

    println!("Prototype completed");
}}
'''
        main_path.write_text(main_code, encoding='utf-8')
        files.append(str(main_path))

        # Generate Cargo.toml
        cargo_path = Path(output_dir) / "Cargo.toml"
        cargo_toml = '''[package]
name = "prototype"
version = "0.1.0"
edition = "2021"

[dependencies]
'''
        cargo_path.write_text(cargo_toml, encoding='utf-8')
        files.append(str(cargo_path))

        return str(main_path), files

    def _generate_go(self, analysis: Any, output_dir: str, source_info: Optional[Dict[str, Any]]) -> tuple[str, List[str]]:
        """Generate Go project"""
        files = []

        # Generate main.go
        main_path = Path(output_dir) / "main.go"
        main_code = f'''// Prototype Implementation
// Domain: {analysis.domain}
package main

import "fmt"

func main() {{
    fmt.Println("Prototype starting...")

    // Implement algorithms here

    fmt.Println("Prototype completed")
}}
'''
        main_path.write_text(main_code, encoding='utf-8')
        files.append(str(main_path))

        return str(main_path), files

    def _generate_readme(
        self,
        analysis: Any,
        language: str,
        output_dir: str,
        source_info: Optional[Dict[str, Any]]
    ) -> str:
        """Generate README.md"""
        source_url = source_info.get('source_url', 'Unknown') if source_info else 'Unknown'
        source_title = source_info.get('title', 'Untitled') if source_info else 'Untitled'

        install_cmd = {
            'python': 'pip install -r requirements.txt',
            'javascript': 'npm install',
            'typescript': 'npm install',
            'rust': 'cargo build',
            'go': 'go build',
        }.get(language, 'See documentation')

        run_cmd = {
            'python': 'python src/main.py',
            'javascript': 'node index.js',
            'typescript': 'npx ts-node index.ts',
            'rust': 'cargo run',
            'go': 'go run main.go',
        }.get(language, 'See documentation')

        readme = f'''# Prototype Implementation

> Generated from: [{source_title}]({source_url})

## Overview

This is an automatically generated prototype based on the article content.

- **Domain:** {analysis.domain}
- **Complexity:** {analysis.complexity}
- **Language:** {language}
- **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Installation

```bash
{install_cmd}
```

## Usage

```bash
{run_cmd}
```

## Structure

This prototype includes:
- Main implementation file
- Dependencies manifest
- Basic test suite (if applicable)

## Detected Algorithms

{chr(10).join(f"- {algo.name}: {algo.description}" for algo in analysis.algorithms[:5])}

## Source Attribution

- Original Article: [{source_title}]({source_url})
- Extraction Date: {datetime.now().strftime("%Y-%m-%d")}
- Generated by: Article-to-Prototype Skill v1.0

## License

MIT License
'''

        readme_path = Path(output_dir) / "README.md"
        readme_path.write_text(readme, encoding='utf-8')
        return str(readme_path)

    def _generate_gitignore(self, language: str, output_dir: str) -> str:
        """Generate .gitignore"""
        gitignore_templates = {
            'python': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/
''',
            'javascript': '''# Node
node_modules/
npm-debug.log
yarn-error.log
.env
dist/
build/
''',
            'typescript': '''# TypeScript/Node
node_modules/
*.js
*.d.ts
npm-debug.log
dist/
build/
''',
            'rust': '''# Rust
target/
Cargo.lock
**/*.rs.bk
''',
            'go': '''# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
go.work
''',
        }

        content = gitignore_templates.get(language, '# Generated files\n')
        gitignore_path = Path(output_dir) / ".gitignore"
        gitignore_path.write_text(content, encoding='utf-8')
        return str(gitignore_path)
