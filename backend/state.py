def parse_dialogue(text):
    if not isinstance(text, str):
        return []

    dialogue = []
    for line in text.splitlines():
        if ":" in line:
            speaker, msg = line.split(":", 1)
            dialogue.append((speaker.strip(), msg.strip()))
    return dialogue



def extract_ai_text(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    return str(content)
