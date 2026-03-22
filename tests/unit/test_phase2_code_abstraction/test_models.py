"""Unit tests for Phase 2 data models."""

import pytest

from archguard.phase2_code_abstraction.models import (
    CallTrace,
    ClassDefinition,
    ImplementationGraph,
    MethodCall,
    MethodDefinition,
)


class TestMethodDefinition:
    def test_init(self):
        method = MethodDefinition("get_user", "UserService", 15)
        assert method.name == "get_user"
        assert method.class_name == "UserService"
        assert method.line_number == 15

    def test_with_parameters(self):
        method = MethodDefinition("save_user", "UserService", 20, ["user_id", "data"])
        assert len(method.parameters) == 2
        assert "user_id" in method.parameters

    def test_hashable(self):
        m1 = MethodDefinition("get", "Service", 1)
        m2 = MethodDefinition("get", "Service", 5)
        assert hash(m1) == hash(m2)

    def test_in_set(self):
        m1 = MethodDefinition("get", "Service", 1)
        m2 = MethodDefinition("save", "Service", 10)
        method_set = {m1, m2}
        assert len(method_set) == 2


class TestClassDefinition:
    def test_init(self):
        cls = ClassDefinition("UserService", "service.py", 5)
        assert cls.name == "UserService"
        assert cls.file_path == "service.py"
        assert cls.line_number == 5

    def test_with_bases(self):
        cls = ClassDefinition("UserService", "service.py", 5, ["BaseService"])
        assert len(cls.base_classes) == 1

    def test_add_method(self):
        cls = ClassDefinition("UserService", "service.py", 5)
        method = MethodDefinition("get_user", "UserService", 10)
        cls.add_method(method)
        assert "get_user" in cls.methods

    def test_multiple_methods(self):
        cls = ClassDefinition("UserService", "service.py", 5)
        m1 = MethodDefinition("get_user", "UserService", 10)
        m2 = MethodDefinition("save_user", "UserService", 20)
        cls.add_method(m1)
        cls.add_method(m2)
        assert len(cls.methods) == 2

    def test_hashable(self):
        c1 = ClassDefinition("UserService", "s1.py", 5)
        c2 = ClassDefinition("UserService", "s2.py", 10)
        assert hash(c1) == hash(c2)

    def test_with_layer(self):
        cls = ClassDefinition("UserService", "service.py", 5, layer="Service")
        assert cls.layer == "Service"


class TestMethodCall:
    def test_init(self):
        call = MethodCall("UserController", "get_user", "UserService")
        assert call.source_class == "UserController"
        assert call.target_class == "UserService"

    def test_with_target_method(self):
        call = MethodCall("UC", "m1", "US", target_method="fetch")
        assert call.target_method == "fetch"

    def test_call_types(self):
        c_inst = MethodCall("A", "m1", "B", call_type="instance")
        c_stat = MethodCall("A", "m1", "B", call_type="static")
        assert c_inst.call_type == "instance"
        assert c_stat.call_type == "static"

    def test_hashable(self):
        c1 = MethodCall("A", "m1", "B", "m2")
        c2 = MethodCall("A", "m1", "B", "m2")
        assert hash(c1) == hash(c2)

    def test_in_set(self):
        c1 = MethodCall("A", "m1", "B")
        c2 = MethodCall("A", "m1", "C")
        call_set = {c1, c2}
        assert len(call_set) == 2


class TestCallTrace:
    def test_init(self):
        trace = CallTrace()
        assert len(trace) == 0

    def test_add_call(self):
        trace = CallTrace()
        call = MethodCall("A", "m1", "B")
        trace.add_call(call)
        assert len(trace) == 1

    def test_multiple_calls(self):
        trace = CallTrace()
        trace.add_call(MethodCall("A", "m1", "B"))
        trace.add_call(MethodCall("B", "m2", "C"))
        trace.add_call(MethodCall("C", "m3", "D"))
        assert len(trace) == 3

    def test_with_description(self):
        trace = CallTrace(description="Flow")
        assert trace.description == "Flow"


class TestImplementationGraph:
    def test_init(self):
        graph = ImplementationGraph()
        assert len(graph.classes) == 0
        assert len(graph.calls) == 0

    def test_add_class(self):
        graph = ImplementationGraph()
        cls = ClassDefinition("UserService", "service.py", 5)
        graph.add_class(cls)
        assert "UserService" in graph.classes

    def test_add_multiple_classes(self):
        graph = ImplementationGraph()
        graph.add_class(ClassDefinition("UC", "c.py", 1))
        graph.add_class(ClassDefinition("US", "s.py", 5))
        graph.add_class(ClassDefinition("UR", "r.py", 10))
        assert len(graph.classes) == 3

    def test_add_call(self):
        graph = ImplementationGraph()
        graph.add_class(ClassDefinition("A", "a.py", 1))
        graph.add_class(ClassDefinition("B", "b.py", 2))
        graph.add_call(MethodCall("A", "m1", "B"))
        assert len(graph.calls) == 1

    def test_get_called_by(self):
        graph = ImplementationGraph()
        graph.add_class(ClassDefinition("A", "a.py", 1))
        graph.add_class(ClassDefinition("B", "b.py", 2))
        graph.add_class(ClassDefinition("C", "c.py", 3))
        graph.add_call(MethodCall("A", "m1", "B"))
        graph.add_call(MethodCall("A", "m2", "C"))
        targets = graph.get_classes_called_by("A")
        assert len(targets) == 2

    def test_get_callers(self):
        graph = ImplementationGraph()
        graph.add_class(ClassDefinition("A", "a.py", 1))
        graph.add_class(ClassDefinition("C", "c.py", 3))
        graph.add_call(MethodCall("A", "m1", "C"))
        callers = graph.get_callers_of("C")
        assert len(callers) == 1

    def test_has_call(self):
        graph = ImplementationGraph()
        graph.add_class(ClassDefinition("A", "a.py", 1))
        graph.add_class(ClassDefinition("B", "b.py", 2))
        graph.add_call(MethodCall("A", "m1", "B"))
        assert graph.has_call("A", "B")
        assert not graph.has_call("B", "A")

    def test_networkx_export(self):
        graph = ImplementationGraph()
        graph.add_class(ClassDefinition("A", "a.py", 1))
        graph.add_class(ClassDefinition("B", "b.py", 2))
        graph.add_call(MethodCall("A", "m1", "B"))
        nx_graph = graph.to_networkx()
        assert "A" in nx_graph.nodes()
        assert nx_graph.has_edge("A", "B")

    def test_complex_graph(self):
        graph = ImplementationGraph()
        graph.add_class(ClassDefinition("UC", "c.py", 1, layer="UI"))
        graph.add_class(ClassDefinition("US", "s.py", 5, layer="Service"))
        graph.add_class(ClassDefinition("UR", "r.py", 10, layer="Data"))
        graph.add_call(MethodCall("UC", "get", "US"))
        graph.add_call(MethodCall("US", "fetch", "UR"))
        assert len(graph.classes) == 3
        assert len(graph.calls) == 2

    def test_graph_length(self):
        graph = ImplementationGraph()
        assert len(graph) == 0
        graph.add_class(ClassDefinition("A", "a.py", 1))
        assert len(graph) == 1
