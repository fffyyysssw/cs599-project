from __future__ import annotations

from typing import Any

from app.ai.llm_client import LLMClient
from app.ai.mock_engine import (
    classify_intent,
    extract_entities,
    generate_summary,
    generate_title,
    get_missing_fields,
)
from app.ai.prompts import build_extraction_prompt, build_intent_prompt, build_summary_prompt
from app.ai.state import WorkflowState
from app.utils.helpers import build_risk_tips, determine_approval_route, determine_required_materials


client = LLMClient()


def intent_classifier(state: WorkflowState) -> dict[str, Any]:
    if client.enabled:
        try:
            result = client.chat_json(build_intent_prompt(state["user_input"]))
            process_type = result.get("process_type")
            confidence = float(result.get("confidence", 0.8))
            if process_type in {"leave", "reimbursement", "purchase"}:
                return {"process_type": process_type, "confidence": round(confidence, 2)}
        except Exception:
            pass
    process_type, confidence = classify_intent(state["user_input"])
    return {"process_type": process_type, "confidence": confidence}


def entity_extractor(state: WorkflowState) -> dict[str, Any]:
    process_type = state.get("process_type") or "leave"
    if client.enabled:
        try:
            result = client.chat_json(build_extraction_prompt(state["user_input"], process_type))
            if isinstance(result, dict):
                return {"extracted_fields": result}
        except Exception:
            pass
    return {"extracted_fields": extract_entities(state["user_input"], process_type)}


def rule_checker(state: WorkflowState) -> dict[str, Any]:
    process_type = state.get("process_type") or "leave"
    extracted_fields = state.get("extracted_fields") or {}
    missing_fields = get_missing_fields(process_type, extracted_fields)
    required_materials = determine_required_materials(process_type, extracted_fields)
    risk_tips = build_risk_tips(process_type, extracted_fields, required_materials)
    return {
        "missing_fields": missing_fields,
        "required_materials": required_materials,
        "risk_tips": risk_tips,
    }


def route_planner(state: WorkflowState) -> dict[str, Any]:
    process_type = state.get("process_type") or "leave"
    extracted_fields = state.get("extracted_fields") or {}
    approval_route = determine_approval_route(process_type, extracted_fields)
    return {"approval_route": approval_route}


def summary_generator(state: WorkflowState) -> dict[str, Any]:
    process_type = state.get("process_type") or "leave"
    extracted_fields = state.get("extracted_fields") or {}
    missing_fields = state.get("missing_fields") or []
    required_materials = state.get("required_materials") or []
    approval_route = state.get("approval_route") or []
    risk_tips = state.get("risk_tips") or []

    fallback = {
        "title": generate_title(process_type, extracted_fields),
        "summary": generate_summary(
            process_type,
            extracted_fields,
            missing_fields,
            required_materials,
            approval_route,
            risk_tips,
        ),
    }
    if client.enabled:
        try:
            result = client.chat_json(
                build_summary_prompt(
                    {
                        "process_type": process_type,
                        "extracted_fields": extracted_fields,
                        "missing_fields": missing_fields,
                        "required_materials": required_materials,
                        "approval_route": approval_route,
                        "risk_tips": risk_tips,
                    }
                )
            )
            if result.get("title") and result.get("summary"):
                return {"title": result["title"], "summary": result["summary"]}
        except Exception:
            pass
    return fallback


def response_formatter(state: WorkflowState) -> dict[str, Any]:
    final_response = {
        "process_type": state.get("process_type") or "leave",
        "confidence": round(float(state.get("confidence") or 0), 2),
        "title": state.get("title") or "",
        "extracted_fields": state.get("extracted_fields") or {},
        "missing_fields": state.get("missing_fields") or [],
        "required_materials": state.get("required_materials") or [],
        "approval_route": state.get("approval_route") or [],
        "risk_tips": state.get("risk_tips") or [],
        "summary": state.get("summary") or "",
    }
    return {"final_response": final_response}
