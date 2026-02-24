# src/decision/policy.py

def decide_action(intent, context_reasons):
    """
    intent: dict from pdf_intent
    context_reasons: list from file_context
    """

    if intent["has_execution_intent"] and "OpenAction" in intent["indicators"]:
        return "HIGH", "SANDBOX"

    if intent["has_execution_intent"]:
        return "MEDIUM", "CDR"

    if context_reasons:
        return "MEDIUM", "CDR"

    return "LOW", "NONE"
