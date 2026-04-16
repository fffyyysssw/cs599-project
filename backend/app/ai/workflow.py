from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.ai.nodes import (
    entity_extractor,
    intent_classifier,
    response_formatter,
    route_planner,
    rule_checker,
    summary_generator,
)
from app.ai.state import WorkflowState


def build_workflow():
    graph = StateGraph(WorkflowState)
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("entity_extractor", entity_extractor)
    graph.add_node("rule_checker", rule_checker)
    graph.add_node("route_planner", route_planner)
    graph.add_node("summary_generator", summary_generator)
    graph.add_node("response_formatter", response_formatter)

    graph.add_edge(START, "intent_classifier")
    graph.add_edge("intent_classifier", "entity_extractor")
    graph.add_edge("entity_extractor", "rule_checker")
    graph.add_edge("rule_checker", "route_planner")
    graph.add_edge("route_planner", "summary_generator")
    graph.add_edge("summary_generator", "response_formatter")
    graph.add_edge("response_formatter", END)

    return graph.compile()


workflow = build_workflow()


def analyze_text(text: str) -> dict:
    state: WorkflowState = {
        "user_input": text,
        "process_type": None,
        "confidence": None,
        "extracted_fields": None,
        "missing_fields": None,
        "required_materials": None,
        "risk_tips": None,
        "approval_route": None,
        "title": None,
        "summary": None,
        "final_response": None,
        "error": None,
    }
    result = workflow.invoke(state)
    return result["final_response"]
