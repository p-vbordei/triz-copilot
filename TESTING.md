# TRIZ System Testing

## Test Suite Overview

**Total Tests: 56 (100% passing ✅)**

The TRIZ system has a comprehensive test suite covering all core functionality:

### Test Structure

```
tests/
├── contract/           # Contract tests (20 tests)
│   ├── test_solve_contract_green.py
│   ├── test_tools_contract_green.py
│   └── test_workflow_contract_green.py
├── integration/        # Integration tests (17 tests)
│   └── test_complete_system.py
├── unit/              # Unit tests (10 tests)
│   └── test_models.py
└── validation/        # System validation (9 tests)
    └── test_system_health.py
```

## Running Tests

### Run All Tests
```bash
uv run python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Contract tests (API contracts)
uv run python -m pytest tests/contract/ -v

# Integration tests (end-to-end workflows)
uv run python -m pytest tests/integration/ -v

# Unit tests (individual components)
uv run python -m pytest tests/unit/ -v

# Validation tests (system health & performance)
uv run python -m pytest tests/validation/ -v
```

### Quick Test
```bash
# Run with minimal output
uv run python -m pytest tests/ -q
```

## Test Coverage

### Contract Tests (20 tests)
- ✅ Autonomous solve functionality
- ✅ Workflow start/continue/reset
- ✅ Direct tool access (principles, contradiction matrix)
- ✅ Input validation
- ✅ Error handling

### Integration Tests (17 tests)
- ✅ Complete solve workflows
- ✅ Multi-step guided workflows
- ✅ Workflow state management
- ✅ Data integrity (principles, matrix, materials)
- ✅ End-to-end problem solving

### Unit Tests (10 tests)
- ✅ TRIZToolResponse model
- ✅ ProblemSession model (create, save, load, reset)
- ✅ Session stage advancement
- ✅ TRIZPrinciple model
- ✅ ContradictionResult model
- ✅ Workflow enums

### Validation Tests (9 tests)
- ✅ Qdrant vector database connectivity
- ✅ Ollama embeddings availability
- ✅ Knowledge base loading
- ✅ Contradiction matrix loading
- ✅ Core module imports
- ✅ Data file existence
- ✅ Response time benchmarks (solve, workflow, tools)

## Test Quality Metrics

- **Pass Rate**: 100% (56/56)
- **Code Coverage**: Core functionality fully tested
- **Performance**: All operations complete within acceptable time limits
  - Solve: < 30 seconds
  - Workflow start: < 2 seconds
  - Tool access: < 1 second

## Prerequisites

### Required Services
- **Qdrant**: Vector database on port 6333
  ```bash
  docker run -d -p 6333:6333 qdrant/qdrant
  ```

- **Ollama**: Embeddings service with nomic-embed-text
  ```bash
  ollama serve
  ollama pull nomic-embed-text
  ```

### Data Initialization
```bash
# Run once to populate collections
uv run python src/triz_tools/setup/knowledge_ingestion.py
uv run python src/triz_tools/setup/materials_ingestion.py --create-default
```

## Test Development

### Adding New Tests

1. **Contract Tests**: Add to appropriate `*_green.py` file
2. **Integration Tests**: Add to `test_complete_system.py`
3. **Unit Tests**: Add to `test_models.py` or create new test file
4. **Validation Tests**: Add to `test_system_health.py`

### Test Fixtures

Available fixtures (from `conftest.py`):
- `temp_dir`: Temporary directory for file operations
- `sample_problem`: Standard test problem statement
- `complex_problem`: Multi-faceted problem for advanced testing

## CI/CD Integration

Tests can be run in CI/CD pipelines with:

```yaml
test:
  script:
    - docker run -d -p 6333:6333 qdrant/qdrant
    - ollama serve &
    - ollama pull nomic-embed-text
    - uv sync
    - uv run python src/triz_tools/setup/qdrant_setup.py
    - uv run python src/triz_tools/setup/knowledge_ingestion.py
    - uv run python src/triz_tools/setup/materials_ingestion.py --create-default
    - uv run python -m pytest tests/ -v
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "Qdrant not accessible"
- **Solution**: Ensure Qdrant is running on port 6333

**Issue**: Tests fail with "Ollama not available"
- **Solution**: Start Ollama service and verify nomic-embed-text model is installed

**Issue**: Knowledge base tests fail
- **Solution**: Run knowledge ingestion scripts to populate data

### Debug Mode

Run tests with verbose output and traceback:
```bash
uv run python -m pytest tests/ -vv --tb=long
```

## Test Results History

| Date | Tests | Pass | Fail | Coverage |
|------|-------|------|------|----------|
| 2025-10-02 | 56 | 56 | 0 | 100% |

## Next Steps

The test suite is comprehensive and all tests pass. For additional testing:

1. **Performance Testing**: Add load tests for concurrent users
2. **Stress Testing**: Test with very large problems (10,000+ characters)
3. **Edge Cases**: Add more boundary condition tests
4. **Security Testing**: Add input sanitization tests

---

**Status**: ✅ All tests passing
**Last Updated**: October 2, 2025
**Maintainer**: TRIZ Engineering Co-Pilot Team
