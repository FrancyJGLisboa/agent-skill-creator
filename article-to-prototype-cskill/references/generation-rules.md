# Generation Rules Reference

## Code Generation Principles

### 1. Completeness
- No TODO comments
- No placeholder functions
- All imports present
- Full error handling

### 2. Quality Standards
- Type hints/annotations where supported
- Docstrings/documentation comments
- Logging at appropriate levels
- Clean variable names

### 3. Structure
- Follow language conventions
- Standard directory layout
- Separation of concerns
- Testable architecture

## Language-Specific Rules

### Python
- **File**: `src/main.py`
- **Dependencies**: `requirements.txt`
- **Tests**: `tests/test_main.py`
- **Style**: PEP 8 compliant
- **Type Hints**: Required for functions
- **Docstrings**: Google or NumPy style

### JavaScript/TypeScript
- **File**: `index.js` or `index.ts`
- **Dependencies**: `package.json`
- **Style**: Standard or ESLint
- **Modules**: ES6 or CommonJS
- **Exports**: Named and default exports

### Rust
- **File**: `src/main.rs`
- **Dependencies**: `Cargo.toml`
- **Tests**: Inline with `#[cfg(test)]`
- **Documentation**: `///` comments
- **Error Handling**: Result types

### Go
- **File**: `main.go`
- **Package**: `package main`
- **Error Handling**: Explicit error returns
- **Tests**: `_test.go` files

## Project Structure Rules

### Minimum Files
1. Main implementation file
2. Dependency manifest
3. README.md
4. .gitignore

### Recommended Files
5. Test suite
6. Configuration examples
7. License file
8. Documentation

## README Generation Rules

### Required Sections
1. **Title**: Project name
2. **Overview**: Brief description with source attribution
3. **Installation**: Platform-specific instructions
4. **Usage**: Basic examples
5. **Source Attribution**: Link to original article

### Optional Sections
- Implementation Details
- Testing Instructions
- API Documentation
- Troubleshooting

## Dependency Management

### Strategies
1. Extract from analysis dependencies
2. Add based on domain (ML → numpy, pandas)
3. Include only necessary deps
4. Pin versions where possible

### Defaults by Domain
- **ML**: numpy, pandas, scikit-learn
- **Web**: requests, flask/express
- **Data**: pandas, matplotlib

## Error Handling Strategy

### Python
```python
try:
    operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### TypeScript
```typescript
try {
    operation();
} catch (error) {
    console.error('Operation failed:', error);
    throw error;
}
```

### Rust
```rust
fn operation() -> Result<T, Error> {
    // Use ? operator for propagation
    let result = risky_call()?;
    Ok(result)
}
```

## Testing Generation Rules

### Test Structure
- At least one integration test (main execution)
- Placeholder tests for expansion
- Example assertions
- Clear test names

### Python Example
```python
def test_main_execution():
    """Test that main runs without errors"""
    try:
        main()
        assert True
    except Exception as e:
        pytest.fail(f"Execution failed: {e}")
```

## Documentation Rules

### Inline Comments
- Explain non-obvious logic
- Avoid stating the obvious
- Link to source article concepts
- Include complexity notes

### Function Documentation
- Purpose/description
- Parameters with types
- Return value
- Exceptions raised
- Examples (optional)

## Source Attribution Rules

### Required Information
- Original article title
- Article URL or path
- Extraction date
- Generator tool version

### Placement
- File headers
- README overview
- Main function docstring
