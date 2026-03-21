"""Data models for Phase 4: Neuro-Symbolic Handoff."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Explanation:
    """Natural language explanation of a violation."""

    violation_type: str
    source_class: str
    target_class: str
    explanation: str
    severity: str = "high"


@dataclass
class CodeFix:
    """Suggested code fix for a violation."""

    violation_id: str
    original_code: str
    suggested_code: str
    explanation: str
    priority: int = 1


@dataclass
class LLMResponse:
    """Structured LLM response with explanation and fixes."""

    explanations: List[Explanation] = field(default_factory=list)
    code_fixes: List[CodeFix] = field(default_factory=list)
    summary: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
