import openai

# List of API keys to check
api_keys = []
valid_keys = []


def is_valid_key(api_key: str) -> bool:
    """Check if an OpenAI API key is valid by making a test request."""
    try:
        openai.api_key = api_key
        # Lightweight test request
        openai.models.list()
        return True
    except Exception as e:
        print(f"Key {api_key[:10]}... is invalid: {e}")
        return False


def filter_valid_keys(keys: list[str]) -> list[str]:
    """Return only valid keys."""

    for key in keys:
        if is_valid_key(key):
            valid_keys.append(key)
    return valid_keys


if __name__ == "__main__":
    print("Checking API keys...")
    valid_keys = filter_valid_keys(api_keys)
    print("\nValid keys:")
    for vk in valid_keys:
        print(vk)
