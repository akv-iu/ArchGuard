# ArchGuard

ArchGuard is a course project prototype for detecting architectural drift in Python code. It represents an intended architecture as a directed graph, extracts implementation-level dependencies from Python source code, and compares the two graphs to identify calls that violate the architecture specification.

The project is framed as a neuro-symbolic system, but the current repository is mostly the symbolic portion of that system. Phase 4 contains placeholder modules for LLM-based explanation generation and is not yet a working Gemini integration.

## Current Status

Implemented or partially implemented:

- Phase 1: PlantUML architecture parsing.
- Phase 1: Architecture graph construction with NetworkX.
- Phase 2: Python source parsing using Python's built-in `ast` module.
- Phase 2: Extraction of classes, methods, method calls, and implementation dependency graphs.
- Phase 3: Deterministic constraint checking between architecture and implementation graphs.
- Phase 3: Direct, transitive, and circular violation models.
- Phase 3: JSON-like and human-readable trace/report generation utilities.
- Phase 4: Data models and placeholder classes for prompts, Gemini calls, and explanation formatting.

Not currently implemented:

- A working end-to-end `ArchGuard` facade in `src/archguard/core.py`.
- A packaged command-line command such as `archguard analyze`.
- Real Gemini API calls.
- Real prompt generation or response parsing for Phase 4.
- Multi-language parsing beyond Python.
- Production-scale evaluation on large repositories.
- A complete example application in the `examples/` directory.

## Repository Layout

```text
ArchGuard/
  src/archguard/
    common/
      Shared exceptions, constants, logging, and graph helpers.
    phase1_symbolic_brain/
      PlantUML parsing, architecture models, and architecture graph builder.
    phase2_code_abstraction/
      Python AST parsing, code fact extraction, and implementation graph builder.
    phase3_logic_engine/
      Constraint checking, violation detection, trace generation, and reports.
    phase4_neuro_symbolic/
      Placeholder Gemini client, prompt generator, explanation formatter, and models.
    core.py
      Intended top-level orchestrator, currently mostly placeholder code.
  tests/
    unit/
      Unit tests for phases 1, 2, and 3.
    integration/
      End-to-end tests for the implemented phase-level pipelines.
    fixtures/
      Sample PlantUML architectures and Python source files.
```

## Installation

Requirements:

- Python 3.10 or newer.
- `pip`.

Set up the project:

```bash
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev]"
```

On macOS or Linux, activate the virtual environment with:

```bash
source venv/bin/activate
```

## Running Tests

Run the test suite:

```bash
pytest -q
```

Latest local test run:

```text
Command: .\venv\Scripts\python.exe -m pytest -q
Environment: Windows, Python 3.13.7, pytest 9.0.2
Collected: 254 tests
Result: 214 passed, 40 errors
```

Important note: the 40 errors in the latest run were setup-time `PermissionError` failures when pytest tried to create temporary directories under:

```text
C:\Users\aksha\AppData\Local\Temp\pytest-of-aksha
```

These errors affected tests that use pytest temporary fixtures such as `tmp_path`. In the same run, the Phase 3 integration and unit tests completed successfully. Because the temp-directory issue prevents the full suite from running cleanly in this environment, this README does not claim a final passing percentage.

## Using the Implemented Components

The top-level `ArchGuard` class in `core.py` is not yet functional. Use the phase-level modules directly for now.

### Parse a PlantUML Architecture

```python
from archguard.phase1_symbolic_brain.plantuml_parser import PlantUMLParser
from archguard.phase1_symbolic_brain.graph_builder import GraphBuilder

parser = PlantUMLParser()
parsed = parser.parse("tests/fixtures/sample_architectures/simple_layered.puml")

architecture_graph = GraphBuilder.build_from_parsed(parsed)
```

### Extract a Python Implementation Graph

```python
from archguard.phase2_code_abstraction.extractors.python_extractor import PythonExtractor
from archguard.phase2_code_abstraction.code_graph_builder import CodeGraphBuilder

extractor = PythonExtractor()
extraction = extractor.extract_from_file("tests/fixtures/sample_code/simple_service.py")

implementation_graph = CodeGraphBuilder.build_from_extracted(
    extraction,
    "tests/fixtures/sample_code/simple_service.py",
)
```

### Detect Violations

```python
from archguard.phase3_logic_engine.constraint_checker import ConstraintChecker
from archguard.phase3_logic_engine.violation_detector import ViolationDetector

checker = ConstraintChecker(architecture_graph, implementation_graph)
direct_violations = checker.find_violations()

all_violations = ViolationDetector.detect(architecture_graph, implementation_graph)
```

The exact method names may vary across phase modules as the code is still a prototype. The test files under `tests/unit/` and `tests/integration/` are currently the most reliable examples of supported usage.

## Design Decisions

### PlantUML as the Architecture Input

ArchGuard uses PlantUML because it is text-based, version-control friendly, and easy to pair with a source repository. This lets an architecture diagram become a lightweight knowledge base.

Effect on performance and implementation: the current parser uses regular expressions, which keeps the implementation simple and fast for course-sized examples. The tradeoff is that it only supports the PlantUML patterns covered by the parser and tests; it is not a complete PlantUML grammar.

### Graphs as the Shared Representation

Both the intended architecture and the extracted implementation are represented as directed graphs. A node represents a class or component, and an edge represents an allowed or observed dependency.

Effect on performance and implementation: direct violation checking is simple and deterministic because the core operation is edge membership. This gives predictable behavior and makes the reasoning easy to inspect. The tradeoff is that the quality of the result depends heavily on how accurately the architecture and implementation graphs are built.

### Python `ast` Instead of Tree-Sitter in the Current Code

The repository includes `tree-sitter` as a dependency, but the current parser wrapper uses Python's built-in `ast` module for Python source code.

Effect on performance and implementation: `ast` avoids extra parser setup and is enough for Python-only experiments. The tradeoff is that Java, TypeScript, Go, and other languages are not currently supported, and the system cannot claim language-agnostic parsing yet.

### Deterministic Symbolic Detection Before Neural Explanation

The intended architecture is that symbolic code detects violations first, and an LLM explains already-detected violations afterward.

Effect on performance and implementation: Phase 3 is deterministic and does not depend on API latency. Phase 4 would add developer-friendly explanations, but it is not currently implemented, so the repository should not claim working LLM explanations.

### Modular Phases

The project is split into four phases so each phase can be developed and tested separately.

Effect on performance and implementation: this made the test suite easier to organize and made Phase 3 independently usable. The tradeoff is that the project currently lacks a completed orchestrator that connects all phases into one user-facing workflow.

## Known Limitations

- The top-level pipeline in `core.py` is incomplete.
- The command-line examples from earlier project drafts are not currently supported as installed commands.
- Phase 4 is a scaffold, not a working Gemini integration.
- The system only analyzes explicit Python call relationships that the AST extractor can see.
- It does not analyze runtime dispatch, reflection, dependency injection containers, configuration-driven calls, dynamic imports, or generated code.
- The PlantUML parser supports a limited subset of PlantUML syntax.
- The current evaluation is based on small test fixtures, not production-sized repositories.
- The repository has empty `docs/` and `examples/` directories at the time of this README update.
- Current test results are affected by a local pytest temporary-directory permission issue.

## Academic Context

ArchGuard was developed for a knowledge-based AI course project. The project demonstrates:

- Knowledge representation through architecture graphs.
- Constraint checking over symbolic graph structures.
- The intended neuro-symbolic pattern of symbolic detection followed by neural explanation.
- Practical lessons about where deterministic methods are useful in AI-assisted software engineering workflows.

## Code Authorship and External Code

The project code in `src/archguard` and `tests` is project implementation code. External code is used through normal Python package dependencies, including NetworkX, pytest, and Google Generative AI client libraries. No third-party source files are intentionally vendored into this repository.

## Disclaimer About Claims, Assumptions, and Missing Work

This repository should be described as a prototype, not a production-ready tool. The central assumption is that the intended architecture can be represented as a reasonably complete PlantUML dependency graph, and that architectural drift can be detected by comparing explicit implementation edges against that graph. If the specification is incomplete, outdated, or too abstract, ArchGuard may report misleading violations or miss real design problems.

The current implementation also assumes Python source code and mostly explicit call relationships. It does not yet address dynamic language behavior, large repositories, multi-language projects, framework-specific dependency injection, or real developer studies of whether explanations improve comprehension. Claims about scalability, false positives, and usefulness should therefore be limited to the tested fixture setting unless additional experiments are added.

The intended LLM explanation layer is not complete in this codebase. Any project paper or presentation should clearly distinguish implemented symbolic detection from planned or scaffolded Gemini-based explanation.
