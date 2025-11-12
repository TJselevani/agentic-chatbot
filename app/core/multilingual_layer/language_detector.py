from langdetect import detect

class LanguageDetector:
    def detect_language(self, text: str) -> str:
        """
        Detects whether text is in English, Swahili, Sheng, or other.
        Sheng detection is heuristic-based.
        """
        try:
            lang = detect(text)
            # langdetect returns 'sw' for Swahili, 'en' for English
            if lang == "sw":
                return "swahili"
            elif lang == "en":
                # simple heuristic for Sheng (slang-based)
                sheng_terms = ["niko", "msee", "gani", "form", "mambo", "poa", "nash", "sijui"]
                if any(word in text.lower() for word in sheng_terms):
                    return "sheng"
                return "english"
            else:
                return "unknown"
        except Exception:
            return "unknown"
