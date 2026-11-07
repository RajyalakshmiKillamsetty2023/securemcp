_PHRASES = {
    ("hello", "spanish"): "hola",
    ("hello", "french"): "bonjour",
    ("thank you", "spanish"): "gracias",
    ("thank you", "french"): "merci",
}


def run(text: str, target_language: str) -> dict:
    out = _PHRASES.get((text.strip().lower(), target_language.strip().lower()))
    return {"text": text, "target_language": target_language,
            "translation": out or f"[{target_language}] {text}"}
