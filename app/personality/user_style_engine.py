import uuid
from app.personality.personality_store import get_user_styles, append_style
from app.personality.personality_models import UserStyleNode
from app.personality.privacy_filter_engine import filter_sensitive_info

def record_user_style(
    writing_style: str,
    verbosity: str,
    formatting_style: str,
    emoji_usage: bool = False,
    example_text: str = ""
) -> UserStyleNode:
    """
    Analyzes and saves user style behaviors. Applies sensitive filtering firewall.
    """
    clean_style, _ = filter_sensitive_info(writing_style)
    clean_verb, _ = filter_sensitive_info(verbosity)
    clean_format, _ = filter_sensitive_info(formatting_style)
    clean_example, _ = filter_sensitive_info(example_text)

    styles = get_user_styles()
    node = None
    for s in styles:
        if s.writing_style.lower() == clean_style.lower() and s.formatting_style.lower() == clean_format.lower():
            node = s
            break

    if node is None:
        node = UserStyleNode(
            style_id=f"style_{uuid.uuid4().hex[:8]}",
            writing_style=clean_style,
            verbosity=clean_verb,
            formatting_style=clean_format,
            emoji_usage=emoji_usage,
            examples=[],
            confidence=0.5
        )

    if clean_example and clean_example not in node.examples:
        node.examples.append(clean_example)
        if len(node.examples) > 5:
            node.examples.pop(0)

    # Increment style confidence
    node.confidence = min(node.confidence + 0.05, 1.0)
    append_style(node)
    return node
