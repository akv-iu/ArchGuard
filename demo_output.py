"""
ArchGuard — Annotated Sample Output
====================================
This file was created for easy, self-contained testing and demonstration of the
ArchGuard pipeline. Running it exercises all three implemented phases end-to-end
and produces annotated output suitable for inclusion in a project appendix or PDF.

HOW TO RUN
----------
  # Print to terminal:
  python demo_output.py

  # Capture to file (for PDF):
  python demo_output.py > appendix_output.txt

WHAT THIS FILE DOES
-------------------
The script drives the real ArchGuard source code (src/archguard/) through a series
of representative scenarios, printing labelled output at each step.

  Sections A, B, C, G — REAL PIPELINE
    These sections load actual fixture files from tests/fixtures/ and pass them
    through the live Phase 1 and Phase 2 modules:
      - PlantUMLParser reads .puml files and extracts layers, classes, and edges
      - GraphBuilder converts the parsed data into an ArchitectureGraph (NetworkX)
      - PythonExtractor walks the AST of a real .py file and extracts classes,
        methods, and call relationships
      - CodeGraphBuilder converts those facts into an ImplementationGraph (NetworkX)
      - ViolationDetector.detect() runs the full Phase 3 constraint check

  Sections D, E, F — SYNTHETIC GRAPHS (purpose-built violation demos)
    The real fixture code in simple_service.py is conforming (no violations),
    so these sections manually construct minimal ImplementationGraph objects with
    specific MethodCall entries to demonstrate each violation type in isolation.
    The Phase 3 detection logic (ViolationDetector, TraceGenerator) is still the
    real, unmodified code — only the input graphs are hand-crafted.

WHAT WAS BUILT (summary of implemented work)
---------------------------------------------
  Phase 1 — Architecture Parsing
    PlantUMLParser extracts layers, classes, and directed dependency edges from a
    .puml file using regular expressions.  GraphBuilder produces an ArchitectureGraph
    backed by a NetworkX DiGraph.  Every permitted dependency is a direct edge in
    that graph; transitive reachability does NOT imply permission.

  Phase 2 — Code Extraction
    PythonExtractor uses Python's ast module to walk source files and extract class
    definitions, method signatures, and explicit method-call relationships.
    Constructor aliasing (self.repo = Repository()) is resolved so that downstream
    calls to self.repo.method() are correctly attributed to Repository.
    CodeGraphBuilder converts the extracted facts into an ImplementationGraph.

  Phase 3 — Violation Detection
    ConstraintChecker compares every implementation edge against the architecture
    graph and classifies violations into three types:
      DIRECT_VIOLATION    — an implementation edge (u, v) has no matching arch edge
      TRANSITIVE_VIOLATION — a multi-hop code path contains at least one forbidden hop
      CIRCULAR_DEPENDENCY — the implementation graph contains a cycle
    ViolationDetector.detect() aggregates all three types in a single call.
    TraceGenerator produces both human-readable reports and structured JSON traces
    intended for downstream processing (Phase 4 LLM explanation, not yet active).

  Phase 4 — LLM Explanation (scaffold only, not demonstrated here)
    Data models and placeholder classes exist in phase4_neuro_symbolic/ but the
    Gemini API integration is not yet implemented.
"""

import sys, json, logging
from pathlib import Path

# Ensure we load from this project's src/, not any other installed copy
sys.path.insert(0, str(Path(__file__).parent / "src"))

sys.stdout.reconfigure(encoding="utf-8")
logging.disable(logging.CRITICAL)   # suppress INFO logs for clean output

def section(title):
    bar = "=" * 62
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}\n")

def subsection(title):
    print(f"\n--- {title} ---")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION A  Phase 1: Architecture Parsing
# RUNS: real Phase 1 pipeline on tests/fixtures/sample_architectures/simple_layered.puml
# ─────────────────────────────────────────────────────────────────────────────

section("SECTION A — Phase 1: Architecture Parsing")

from archguard.phase1_symbolic_brain.plantuml_parser import PlantUMLParser
from archguard.phase1_symbolic_brain.graph_builder import GraphBuilder

PUML_FILE = "tests/fixtures/sample_architectures/simple_layered.puml"

subsection("Input: simple_layered.puml")
with open(PUML_FILE) as f:
    print(f.read())

subsection("PlantUMLParser — raw parsed data")
parser = PlantUMLParser()
parsed = parser.parse(PUML_FILE)

print(f"  Layers found  : {list(parsed['layers'].keys())}")
print(f"  Classes found : {list(parsed['classes'].keys())}")
print(f"  Edges found   :")
for e in parsed['edges']:
    print(f"    {e['source']:25s} --> {e['target']}")

subsection("GraphBuilder — ArchitectureGraph (NetworkX)")
arch_graph = GraphBuilder.build_from_parsed(parsed)
nx_arch = arch_graph.to_networkx()

print(f"  Nodes : {sorted(nx_arch.nodes())}")
print(f"  Edges : {sorted(nx_arch.edges())}")
print()
print(f"  is_edge_allowed('UserController', 'UserService')    : "
      f"{arch_graph.is_edge_allowed('UserController', 'UserService')}")
print(f"  is_edge_allowed('UserController', 'UserRepository') : "
      f"{arch_graph.is_edge_allowed('UserController', 'UserRepository')}")
print(f"  get_allowed_targets('UserService') : "
      f"{sorted(arch_graph.get_allowed_targets('UserService'))}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION B  Phase 2: Code Extraction
# RUNS: real Phase 2 pipeline on tests/fixtures/sample_code/simple_service.py
# ─────────────────────────────────────────────────────────────────────────────

section("SECTION B — Phase 2: Code Extraction")

from archguard.phase2_code_abstraction.extractors.python_extractor import PythonExtractor
from archguard.phase2_code_abstraction.code_graph_builder import CodeGraphBuilder

CODE_FILE = "tests/fixtures/sample_code/simple_service.py"

subsection("Input: simple_service.py (first 20 lines)")
with open(CODE_FILE) as f:
    lines = f.readlines()
for i, line in enumerate(lines[:20], 1):
    print(f"  {i:>3}  {line}", end="")
print("  ...")

subsection("PythonExtractor — extracted classes and methods")
extractor = PythonExtractor()
extraction = extractor.extract_from_file(CODE_FILE)

for class_name, cls_data in extraction['classes'].items():
    methods = list(cls_data['methods'].keys())
    print(f"  Class {class_name:20s}  methods: {methods}")

subsection("PythonExtractor — extracted method calls")
for call in extraction['calls']:
    src = f"{call['source_class']}.{call['source_method']}()"
    tgt = f"{call['target_class']}.{call.get('target_method','?')}()"
    print(f"  {src:40s}  -->  {tgt}")

subsection("CodeGraphBuilder — ImplementationGraph (NetworkX)")
impl_graph = CodeGraphBuilder.build_from_extracted(extraction, CODE_FILE)
nx_impl = impl_graph.to_networkx()

print(f"  Nodes : {sorted(nx_impl.nodes())}")
print(f"  Edges : {sorted(nx_impl.edges())}")
print(f"  Total unique calls tracked : {len(impl_graph.calls)}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION C  Phase 3: Conforming Code — No Violations
# RUNS: real Phase 3 detection on the graphs produced by Sections A and B
# ─────────────────────────────────────────────────────────────────────────────

section("SECTION C — Phase 3: Conforming Code (No Violations)")

from archguard.phase3_logic_engine.violation_detector import ViolationDetector
from archguard.phase3_logic_engine.trace_generator import TraceGenerator

subsection("Input: simple_layered.puml + simple_service.py (architecture followed exactly)")
violations_clean = ViolationDetector.detect(arch_graph, impl_graph)
print(f"  Violations detected : {len(violations_clean)}")
print()
print(TraceGenerator.generate_human_readable(violations_clean))


# ─────────────────────────────────────────────────────────────────────────────
# SECTION D  Phase 3: Direct Violation — Layer Bypass
# USES: synthetic ImplementationGraph (hand-crafted to show one bypass call)
# RUNS: real Phase 3 detection — ViolationDetector and TraceGenerator are live code
# ─────────────────────────────────────────────────────────────────────────────

section("SECTION D — Phase 3: Direct Violation — Layer Bypass")

from archguard.phase2_code_abstraction.models import ImplementationGraph, ClassDefinition, MethodCall

subsection("Scenario")
print("  Architecture  : UserController → UserService → UserRepository")
print("  Code (buggy)  : UserController calls UserRepository directly (line 37)")
print("                  bypassing the required UserService layer")

bypass_graph = ImplementationGraph()
for cls in ["UserController", "UserService", "UserRepository"]:
    bypass_graph.add_class(ClassDefinition(cls, "app.py", 0))
bypass_graph.add_call(MethodCall(source_class="UserController", source_method="get_user",   target_class="UserService",    target_method="fetch_user",  line_number=36))
bypass_graph.add_call(MethodCall(source_class="UserService",    source_method="fetch_user", target_class="UserRepository", target_method="find_by_id",  line_number=86))
bypass_graph.add_call(MethodCall(source_class="UserController", source_method="get_user",   target_class="UserRepository", target_method="find_by_id",  line_number=37))

subsection("Human-Readable Violation Report")
violations_bypass = ViolationDetector.detect(arch_graph, bypass_graph)
print(TraceGenerator.generate_human_readable(violations_bypass))

subsection("Structured JSON Trace (sent to Phase 4)")
print(TraceGenerator.generate_json_traces(violations_bypass))


# ─────────────────────────────────────────────────────────────────────────────
# SECTION E  Phase 3: Transitive Violation
# USES: synthetic ArchitectureGraph + synthetic ImplementationGraph
# RUNS: real Phase 3 detection
# ─────────────────────────────────────────────────────────────────────────────

section("SECTION E — Phase 3: Transitive Violation")

from archguard.phase1_symbolic_brain.models import ArchitectureGraph, ArchitectureClass, ArchitectureEdge

subsection("Scenario")
print("  Architecture  : ProductController → ProductService → ProductRepository")
print("  Code (buggy)  : ProductService also calls UserRepository (not in arch)")
print("  Transitive    : ProductController reaches UserRepository via forbidden hop")

arch2 = ArchitectureGraph()
for cls, layer in [("ProductController","ui"), ("ProductService","service"),
                   ("ProductRepository","data"), ("UserRepository","data")]:
    arch2.add_class(ArchitectureClass(cls, layer))
arch2.add_edge(ArchitectureEdge("ProductController", "ProductService",   "calls"))
arch2.add_edge(ArchitectureEdge("ProductService",    "ProductRepository","calls"))

trans_graph = ImplementationGraph()
for cls in ["ProductController", "ProductService", "ProductRepository", "UserRepository"]:
    trans_graph.add_class(ClassDefinition(cls, "product.py", 0))
trans_graph.add_call(MethodCall(source_class="ProductController", source_method="handle",  target_class="ProductService",   target_method="process"))
trans_graph.add_call(MethodCall(source_class="ProductService",   source_method="process", target_class="ProductRepository", target_method="save"))
trans_graph.add_call(MethodCall(source_class="ProductService",   source_method="process", target_class="UserRepository",    target_method="find"))

subsection("Violation Report")
violations_trans = ViolationDetector.detect(arch2, trans_graph)
print(TraceGenerator.generate_human_readable(violations_trans))


# ─────────────────────────────────────────────────────────────────────────────
# SECTION F  Phase 3: Circular Dependency
# USES: synthetic ArchitectureGraph + synthetic ImplementationGraph
# RUNS: real Phase 3 detection including nx.simple_cycles() via ConstraintChecker
# ─────────────────────────────────────────────────────────────────────────────

section("SECTION F — Phase 3: Circular Dependency Detection")

subsection("Scenario")
print("  Code (buggy)  : OrderService.process()       → PaymentService.charge()")
print("                  PaymentService.charge()       → OrderService.update_status()")
print("  This forms a cycle: OrderService → PaymentService → OrderService")

arch3 = ArchitectureGraph()
for cls, layer in [("OrderService","service"), ("PaymentService","service")]:
    arch3.add_class(ArchitectureClass(cls, layer))
arch3.add_edge(ArchitectureEdge("OrderService", "PaymentService", "calls"))

circ_graph = ImplementationGraph()
for cls in ["OrderService", "PaymentService"]:
    circ_graph.add_class(ClassDefinition(cls, "services.py", 0))
circ_graph.add_call(MethodCall(source_class="OrderService",   source_method="process", target_class="PaymentService", target_method="charge",        line_number=12))
circ_graph.add_call(MethodCall(source_class="PaymentService", source_method="charge",  target_class="OrderService",   target_method="update_status", line_number=28))

subsection("Violation Report")
violations_circ = ViolationDetector.detect(arch3, circ_graph)
print(TraceGenerator.generate_human_readable(violations_circ))

subsection("Classification Breakdown")
cls_result = ViolationDetector.classify_violations(violations_circ)
print(f"  Critical (circular)  : {len(cls_result['critical'])}")
print(f"  High (direct)        : {len(cls_result['high'])}")
print(f"  Medium (transitive)  : {len(cls_result['medium'])}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION G  Phase 1: Complex Architecture — ecommerce_arch.puml
# RUNS: real Phase 1 pipeline on tests/fixtures/sample_architectures/ecommerce_arch.puml
# ─────────────────────────────────────────────────────────────────────────────

section("SECTION G — Phase 1: Complex Architecture (ecommerce_arch.puml)")

ECOMM_FILE = "tests/fixtures/sample_architectures/ecommerce_arch.puml"
parsed_ecomm = parser.parse(ECOMM_FILE)
arch_ecomm   = GraphBuilder.build_from_parsed(parsed_ecomm)
nx_ecomm     = arch_ecomm.to_networkx()

print(f"  Layers  : {list(parsed_ecomm['layers'].keys())}")
print(f"  Classes : {sorted(nx_ecomm.nodes())}")
print(f"  Total permitted edges : {nx_ecomm.number_of_edges()}")
print()
print("  Permitted dependency graph:")
for src, tgt in sorted(nx_ecomm.edges()):
    print(f"    {src:25s}  -->  {tgt}")

print("\n" + "=" * 62)
print("  END OF DEMO OUTPUT")
print("=" * 62)
