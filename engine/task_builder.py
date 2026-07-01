"""
Location: engine/task_builder.py
Purpose: Shared task building utilities for leaf prompts
Functions: build_standard_prompt()
Imports: (none)
"""


def build_standard_prompt(system_instruction: str, json_instruction: str, instance: dict) -> str:
    """
    Build a standard task prompt with system instruction and JSON schema.
    Args:
        system_instruction: The system role/task description
        json_instruction: The JSON response schema instruction
        instance: Dict with "document" key containing the excerpt
    Returns: Formatted prompt string
    """
    clause = instance.get("document", "")
    return f"{system_instruction}\n\n{json_instruction}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"
