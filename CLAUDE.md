# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Commands

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src/archguard --cov-report=html

# Run tests by phase
pytest tests/unit/test_phase1_symbolic_brain/      # Phase 1
pytest tests/unit/test_phase2_code_abstraction/    # Phase 2
pytest tests/unit/test_phase3_logic_engine/        # Phase 3

# Run specific test file or test
pytest tests/unit/test_phase1_symbolic_brain/test_plantuml_parser.py
pytest tests/unit/test_phase1_symbolic_brain/test_plantuml_parser.py::test_parse_simple_architecture

# Run by marker
pytest -m unit      # Unit tests only
pytest -m integration # Integration tests
pytest -m e2e       # End-to-end tests
```

### Code Quality
```bash
# Type checking
mypy src/archguard

# Linting
pylint src/archguard

# Code formatting (check)
black --check src/archguard

# Code formatting (apply)
black src/archguard

# Import sorting
isort src/archguard
```

### Development
```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Build distribution
python -m build

# Install just core dependencies
pip install -e .
```

## Architecture Overview

ArchGuard implements a **4-phase deterministic pipeline** that transforms architectural rules into developer-friendly guidance:

### Phase 1: Symbolic Brain → Architecture Graph
- **Input**: PlantUML architecture specification file
- **Processing**: `PlantUMLParser` (regex-based extraction) → `GraphBuilder` (convert to typed objects) → `ArchitectureGraph` (NetworkX DiGraph)
- **Output**: `ArchitectureGraph` object with layers, classes, and allowed edges as source of truth
- **Key Classes**: `Layer`, `ArchitectureClass`, `ArchitectureEdge`, `ArchitectureGraph`
- **Location**: `src/archguard/phase1_symbolic_brain/`

### Phase 2: Code Abstraction → Implementation Graph
- **Input**: Python source code (files or directory)
- **Processing**: 
  - `TreeSitterWrapper` or `ASTWalker` (parse source to AST)
  - `PythonExtractor` (walk AST, extract classes, methods, calls)
  - `CodeGraphBuilder` (convert to typed objects)
  - Result: `ImplementationGraph` (NetworkX DiGraph)
- **Output**: `ImplementationGraph` object capturing all explicit method-to-method calls
- **Key Classes**: `ClassDefinition`, `MethodDefinition`, `MethodCall`, `ImplementationGraph`
- **Location**: `src/archguard/phase2_code_abstraction/`

### Phase 3: Logic Engine → Violations
- **Input**: `ArchitectureGraph` (Phase 1) + `ImplementationGraph` (Phase 2)
- **Processing**: `ConstraintChecker` (traverses impl graph edges, checks against arch graph)
- **Output**: List of `Violation` objects with full call traces
- **Key Classes**: `Violation`, `ViolationTrace`, `ViolationDetector`, `TraceGenerator`
- **Location**: `src/archguard/phase3_logic_engine/`

### Phase 4: Neuro-Symbolic Handoff → Explanations
- **Input**: JSON violation traces
- **Processing**: `GeminiClient` sends violations to Gemini API
- **Output**: Natural language explanations + code fix suggestions
- **Key Classes**: `GeminiClient`, `ExplanationFormatter`, `PromptGenerator`
- **Location**: `src/archguard/phase4_neuro_symbolic/`

## Key Design Patterns

### 1. Graph-Based Architecture
- **Both** architecture and implementation are represented as `NetworkX DiGraph`
- Nodes = classes, Edges = allowed/actual method calls
- This enables: set operations (find violations), path analysis (transitive violations), visualization
- Use `nx` operations directly: `G.has_edge(source, target)`, `nx.has_path(...)`, `nx.ancestors()`, etc.

### 2. Phase Separation & Type-Safe Handoff
Each phase outputs strongly-typed dataclasses:
- Phase 1 → `ArchitectureGraph` (typed wrapper around `nx.DiGraph`)
- Phase 2 → `ImplementationGraph` (typed wrapper around `nx.DiGraph`)
- Phase 3 → `List[Violation]` (frozen dataclasses for hashability)
- Phase 4 → `List[Explanation]` (with explanation + code_fix fields)

This allows independent testing: mock any upstream phase without reimplementing it.

### 3. Modular Extraction Pipeline (Phase 2)
Phase 2 follows a pipeline pattern:
```
SourceCode → Parser (AST) → Walker (extract facts) → Extractor (high-level API) → GraphBuilder (typed objects) → Graph
```
Each step is independently testable with fixture data in `tests/fixtures/sample_code/`.

### 4. Violation Tracing
Every `Violation` includes:
- `violation_path`: Full call chain (tuple of call sites)
- `type`: DIRECT_VIOLATION, TRANSITIVE_VIOLATION, etc.
- `severity`: high/medium/low
- `source_class`, `target_class`: Entry and exit points

This makes violations debuggable—developers can trace the exact call chain.

## Development Workflow

### Adding a Test
1. **Unit tests**: Add to `tests/unit/test_phase*/test_component.py`
2. **Fixtures**: Put sample data in `tests/fixtures/` (Python code, PlantUML profiles)
3. **Integration tests**: Add to `tests/integration/test_phaseX_end_to_end.py`

### Extending a Phase
1. Read the phase's `models.py` to understand data structures
2. Look at existing `test_*.py` files in the unit tests
3. Follow the same pattern: models → implementation → tests
4. Ensure all new functions have type hints and docstrings

### Common Patterns in Testing
- Use `pytest.fixture` for reusable test data (see `tests/conftest.py`)
- Mark tests with `@pytest.mark.unit`, `@pytest.mark.integration`, or `@pytest.mark.e2e`
- Fixtures stored in `tests/fixtures/sample_architectures/` (PlantUML) and `tests/fixtures/sample_code/` (Python)

## File Organization

```
src/archguard/
├── common/                         # Shared utilities
│   ├── exceptions.py               # All custom exceptions
│   ├── logger.py                   # Colored logging (get_logger, set_log_level)
│   ├── constants.py                # Global constants, violation types
│   └── graph_utils.py              # NetworkX helpers (find_cycles, has_path, etc.)
│
├── phase1_symbolic_brain/          # PlantUML → Architecture Graph
│   ├── models.py                   # Layer, ArchitectureClass, ArchitectureEdge, ArchitectureGraph
│   ├── plantuml_parser.py          # Regex-based PlantUML extraction
│   └── graph_builder.py            # Convert parsed PlantUML to ArchitectureGraph
│
├── phase2_code_abstraction/        # Source Code → Implementation Graph
│   ├── models.py                   # ClassDefinition, MethodDefinition, MethodCall, ImplementationGraph
│   ├── tree_sitter_wrapper.py      # (Stub) AST parsing abstraction (Python uses ast module)
│   ├── ast_walker.py               # Walk Python AST, extract classes/methods/calls
│   ├── extractors/
│   │   └── python_extractor.py     # High-level Python extraction API
│   └── code_graph_builder.py       # Convert extracted facts to ImplementationGraph
│
├── phase3_logic_engine/            # Constraint Satisfaction & Violation Detection
│   ├── models.py                   # Violation, ViolationTrace, ViolationReport
│   ├── constraint_checker.py       # Direct + transitive violation detection
│   ├── violation_detector.py       # High-level interface, classification
│   └── trace_generator.py          # JSON export, human-readable reports, fix suggestions
│
├── phase4_neuro_symbolic/          # JSON → Gemini → Explanations
│   ├── models.py                   # Explanation, CodeFix, LLMResponse
│   ├── gemini_client.py            # Google Generative AI client
│   ├── prompt_generator.py         # Build prompts from violations
│   └── explanation_formatter.py    # Format LLM responses
│
└── core.py                         # Main orchestrator (ArchGuard class)

tests/
├── unit/                           # Unit tests per phase
├── integration/                    # Cross-phase tests
├── e2e/                            # Full pipeline tests
├── fixtures/
│   ├── sample_architectures/       # PlantUML files (.puml)
│   └── sample_code/                # Python sample files (.py)
└── conftest.py                     # Shared pytest fixtures
```

## Key Constants & Exceptions

### Common Exceptions (from `common/exceptions.py`)
- `ArchGuardError`: Base exception
- `ParsingError`: PlantUML or code parsing failed
- `ValidationError`: Invalid architecture or code structure
- `ExtractionError`: Code extraction failed
- `ConstraintViolationError`: Violation detected
- `ConfigurationError`: Invalid configuration
- `APIError`: LLM API call failed

### Violation Types (from `common/constants.py`)
- `DIRECT_VIOLATION`: Call exists in code but not in architecture
- `TRANSITIVE_VIOLATION`: Multi-hop path violates architecture
- `LAYER_BYPASS`: Skips intermediate layer
- (Add more as needed)

## Critical Implementation Notes

### Phase 2: Python Code Extraction
- Currently uses Python's `ast` module directly (not Tree-Sitter for Python)
- Handles: class definitions, method definitions, method calls, inheritance, composition patterns
- Must extract: `self.method()` calls, `super()` calls, constructor calls `ClassName()`
- Class name aliasing: Track `repo = Repository()` to map `repo.method()` calls back to `Repository`

### Phase 3: Violation Detection
- **Direct violations**: Edges in implementation graph not in architecture graph
- **Transitive violations**: Paths in implementation that violate layered architecture
- Use `nx.has_path()` to check transitive reachability
- All violations must include full call chain in `violation_path`

### Production Considerations
- Type hints enabled via `mypy` (see `pyproject.toml`)
- Code formatted with `black` (line length 100)
- Imports sorted with `isort` (profile: black)
- Test coverage tracked (pytest-cov)
- Logging uses colored output via `get_logger()` from common module

## Testing Strategy

- **Unit tests**: Test individual components in isolation with mock inputs
- **Integration tests**: Test phases working together (e.g., Phase 1 → Phase 2)
- **E2E tests**: Full pipeline from PlantUML to violations with real fixture data
- **Markers**: Use `@pytest.mark.{unit|integration|e2e}` to categorize tests

## When to Use What

| Task | Tool/Pattern |
|------|----------------|
| Add a violation type | Update `common/constants.py` + add new `Violation.type` value |
| Extract new code language | Create `phase2_code_abstraction/extractors/java_extractor.py` |
| Add graph utility | Add to `common/graph_utils.py` |
| Debug a violation | Check `ViolationTrace.violation_path` for call chain |
| Test a parser | Add fixture in `tests/fixtures/sample_architectures/` |
| Test extraction | Add fixture in `tests/fixtures/sample_code/` |
