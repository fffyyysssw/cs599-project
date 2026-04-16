from typing import Any, Optional, TypedDict


class WorkflowState(TypedDict):
    user_input: str
    process_type: Optional[str]
    confidence: Optional[float]
    extracted_fields: Optional[dict[str, Any]]
    missing_fields: Optional[list[str]]
    required_materials: Optional[list[str]]
    risk_tips: Optional[list[str]]
    approval_route: Optional[list[str]]
    title: Optional[str]
    summary: Optional[str]
    final_response: Optional[dict[str, Any]]
    error: Optional[str]
