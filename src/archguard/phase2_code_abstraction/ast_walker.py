"""AST walker for Phase 2: Code Abstraction.

Walks Python AST to extract class definitions, method definitions, and method calls.
"""

import ast
from typing import Dict, List, Optional, Set, Tuple

from archguard.common.logger import get_logger

logger = get_logger(__name__)


class ASTWalker:
    """Walks Abstract Syntax Tree to extract architectural facts.

    Extracts:
    - Class definitions with base classes
    - Method definitions within classes
    - Method calls between classes
    """

    def __init__(self):
        """Initialize AST walker."""
        self.classes: Dict[str, Dict] = {}
        self.calls: List[Dict] = []
        self.current_class: Optional[str] = None
        self.current_method: Optional[str] = None
        # Track injected dependencies: {class_name: {attr_name: class_with_type}}
        self.class_dependencies: Dict[str, Dict[str, str]] = {}
        logger.info("AST walker initialized")

    def walk(self, parsed_tree) -> Dict:
        """Walk parse tree and extract facts.

        Args:
            parsed_tree: ParsedTree object from TreeSitterWrapper

        Returns:
            Dictionary with 'classes' and 'calls' keys containing extracted facts
        """
        root = parsed_tree.get_root_node()
        self._walk_node(root)

        # Post-process: try to resolve alias class names to actual classes
        self._resolve_class_aliases()

        return {
            "classes": self.classes,
            "calls": self.calls
        }

    def _resolve_class_aliases(self) -> None:
        """Resolve abbreviated class names to actual classes.

        E.g., if we see calls to 'Repo' but 'Repository' exists, resolve them.
        This helps handle cases where parameters are abbreviated.
        """
        actual_classes = set(self.classes.keys())

        for call in self.calls:
            target_class = call.get("target_class")
            if target_class and target_class not in actual_classes:
                # Try to find a matching class
                resolved = self._find_matching_class(target_class, actual_classes)
                if resolved:
                    logger.debug(f"Resolved alias: {target_class} -> {resolved}")
                    call["target_class"] = resolved

    def _find_matching_class(self, alias: str, actual_classes: Set[str]) -> Optional[str]:
        """Try to find a matching actual class for an alias.

        Args:
            alias: Potential alias name
            actual_classes: Set of actual class names

        Returns:
            Matching class name or None
        """
        # Exact match
        if alias in actual_classes:
            return alias

        # Try lowercase match
        alias_lower = alias.lower()
        for cls in actual_classes:
            if cls.lower() == alias_lower:
                return cls

        # Try substring match - if alias is substring of class name
        # E.g., Repo matches Repository
        for cls in actual_classes:
            if alias.lower() in cls.lower():
                return cls

        # Try reverse - if class name is substring of alias
        for cls in actual_classes:
            if cls.lower() in alias.lower():
                return cls

        return None

    def _walk_node(self, node: ast.AST) -> None:
        """Recursively walk AST nodes.

        Args:
            node: Current AST node to process
        """
        if isinstance(node, ast.ClassDef):
            self._extract_class(node)
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            if self.current_class:
                self._extract_method(node)

        # Recursively walk children
        for child in ast.iter_child_nodes(node):
            self._walk_node(child)

    def _extract_class(self, node: ast.ClassDef) -> None:
        """Extract a class definition.

        Args:
            node: ClassDef AST node
        """
        class_name = node.name
        base_classes = [self._get_name(base) for base in node.bases]
        base_classes = [b for b in base_classes if b is not None]

        logger.debug(f"Extracting class: {class_name}")

        # Save current context
        prev_class = self.current_class
        self.current_class = class_name

        # Store class definition
        self.classes[class_name] = {
            "name": class_name,
            "line_number": node.lineno,
            "base_classes": base_classes,
            "methods": {}
        }

        # Initialize dependency tracking for this class
        self.class_dependencies[class_name] = {}

        # Extract __init__ method to identify injected dependencies
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name == "__init__":
                    self._extract_init_dependencies(child, class_name)

        # Extract methods in this class
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._extract_method(child)
            # Also walk for nested class definitions and calls
            self._walk_node(child)

        # Extract calls within the class body
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self._extract_call(child)

        # Restore previous context
        self.current_class = prev_class

    def _extract_init_dependencies(self, init_node: ast.FunctionDef, class_name: str) -> None:
        """Extract dependencies injected via __init__ method.

        Args:
            init_node: __init__ method FunctionDef node
            class_name: Name of the class
        """
        # Look for assignments like self.service = service
        for node in ast.walk(init_node):
            if isinstance(node, ast.Assign):
                # Check if it's self.attribute = something
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == "self":
                            # This is self.attribute = value
                            attr_name = target.attr
                            # Try to get the value being assigned
                            if isinstance(node.value, ast.Name):
                                # Assigned from parameter or variable
                                assigned_to = node.value.id
                                if assigned_to != "self":
                                    # Convert param name to class name
                                    # E.g., service_a -> ServiceA, repo -> Repo
                                    guessed_class = self._param_name_to_class_name(assigned_to)
                                    self.class_dependencies[class_name][attr_name] = guessed_class
                                    logger.debug(
                                        f"Tracked dependency: {class_name}.{attr_name} -> {guessed_class}"
                                    )

    def _param_name_to_class_name(self, param_name: str) -> str:
        """Convert parameter name to likely class name.

        E.g.:
        - service_a -> ServiceA
        - repo -> Repo
        - user_service -> UserService
        - repository -> Repository

        Args:
            param_name: Parameter name (typically lowercase or snake_case)

        Returns:
            Likely class name (PascalCase)
        """
        # Split by underscore
        parts = param_name.split('_')
        # Capitalize each part and join
        class_name = ''.join(part.capitalize() for part in parts)
        return class_name

    def _extract_method(self, node: ast.FunctionDef) -> None:
        """Extract a method definition.

        Args:
            node: FunctionDef AST node
        """
        if not self.current_class:
            return

        method_name = node.name
        logger.debug(f"Extracting method: {self.current_class}.{method_name}")

        # Store method within class
        if self.current_class not in self.classes:
            self.classes[self.current_class] = {
                "name": self.current_class,
                "line_number": 0,
                "base_classes": [],
                "methods": {}
            }

        self.classes[self.current_class]["methods"][method_name] = {
            "name": method_name,
            "line_number": node.lineno
        }

        # Save method context for call extraction
        prev_method = self.current_method
        self.current_method = method_name

        # Extract calls within this method
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self._extract_call(child)

        self.current_method = prev_method

    def _extract_call(self, node: ast.Call) -> None:
        """Extract a method call.

        Args:
            node: Call AST node
        """
        if not self.current_class or not self.current_method:
            return

        target_class, target_method = self._parse_call_target(node)

        if target_class:
            logger.debug(
                f"Extracting call: {self.current_class}.{self.current_method} "
                f"-> {target_class}.{target_method or '?'}"
            )

            self.calls.append({
                "source_class": self.current_class,
                "source_method": self.current_method,
                "target_class": target_class,
                "target_method": target_method,
                "call_type": "instance",
                "line_number": node.lineno
            })

    def _parse_call_target(self, node: ast.Call) -> Tuple[Optional[str], Optional[str]]:
        """Parse a call node to extract target class and method.

        Handles patterns:
        - self.method() -> (current_class, method)
        - obj.method() -> (obj_class, method) where obj_class is looked up from dependencies
        - method() -> (None, method)

        Args:
            node: Call AST node

        Returns:
            Tuple of (target_class, target_method) or (None, None) if pattern not recognized
        """
        if isinstance(node.func, ast.Attribute):
            # self.method() or obj.method()
            attr_name = node.func.attr  # method name

            if isinstance(node.func.value, ast.Name):
                obj_name = node.func.value.id

                # Check if it's self.method()
                if obj_name == "self":
                    return (self.current_class, attr_name)

                # Check if obj_name is a tracked dependency
                if self.current_class in self.class_dependencies:
                    deps = self.class_dependencies[self.current_class]
                    if obj_name in deps:
                        target_class = deps[obj_name]
                        return (target_class, attr_name)

                # Otherwise it's obj.method() - return obj_name as best guess
                return (obj_name, attr_name)

            elif isinstance(node.func.value, ast.Attribute):
                # Chained: obj.something.method()
                # Try to handle self.obj.method() pattern
                base_attr = node.func.value
                if isinstance(base_attr.value, ast.Name) and base_attr.value.id == "self":
                    # self.something.method()
                    attr_obj = base_attr.attr
                    target_method = attr_name

                    # Look up in dependencies
                    if self.current_class in self.class_dependencies:
                        deps = self.class_dependencies[self.current_class]
                        if attr_obj in deps:
                            target_class = deps[attr_obj]
                            return (target_class, target_method)

                    # If not in dependencies, use as-is
                    return (attr_obj, target_method)

                # Otherwise, try to get base object
                base_obj = self._get_attribute_base(node.func.value)
                if base_obj:
                    return (base_obj, attr_name)

        elif isinstance(node.func, ast.Name):
            # Direct function call: method()
            # This is a module-level function, not a class method
            func_name = node.func.id
            return (None, func_name)

        return (None, None)

    def _get_name(self, node: ast.AST) -> Optional[str]:
        """Get name from various AST node types.

        Args:
            node: AST node

        Returns:
            Name as string or None
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Subscript):
            return self._get_name(node.value)
        return None

    def _get_attribute_base(self, node: ast.Attribute) -> Optional[str]:
        """Get the base name of an attribute chain.

        Args:
            node: Attribute AST node

        Returns:
            Base name or None
        """
        if isinstance(node.value, ast.Name):
            return node.value.id
        elif isinstance(node.value, ast.Attribute):
            return self._get_attribute_base(node.value)
        return None
