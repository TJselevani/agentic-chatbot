from deep_translator import GoogleTranslator
from app.core.multilingual_layer.language_detector import LanguageDetector


class Translator:
    def __init__(self):
        self.translators = {
            "sw": GoogleTranslator(source="swahili", target="english"),
            "en": GoogleTranslator(source="english", target="swahili"),
        }
        self.language_detector = LanguageDetector()

    def detect_language(self, text: str):
        """
        Detects the language of the input text.
        Returns a tuple: (detected_language_code, original_text)
        """
        try:
            detected_lang = self.language_detector.detect_language(text)
            return {"input": text, "language": detected_lang}
        except Exception as e:
            return {"input": text, "language": "unknown", "error": str(e)}

    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Translates text to English. Falls back to auto-detect if language is not specified.
        """
        if source_lang in ("en", "english"):
            return text
        elif source_lang in ("sw", "swahili"):
            return self.translators["sw"].translate(text)
        else:
            # Auto detect unknown language → Swahili → English
            text = GoogleTranslator(source="auto", target="swahili").translate(text)
            return GoogleTranslator(source="swahili", target="english").translate(text)

    def detect_and_translate(self, text: str, target_lang: str) -> str:
        """
        Detects the input language automatically and translates it into the target language.
        If the text is already in the target language, it returns the text unchanged.

        Args:
            text (str): The input text to translate.
            target_lang (str): The language code to translate into (e.g., 'sw' for Swahili, 'en' for English).

        Returns:
            str: Translated text.
        """
        # If already in target language, return as-is
        detected_lang = GoogleTranslator(source="auto", target="english").detect(text)
        if detected_lang == target_lang:
            return text

        # Perform translation
        return GoogleTranslator(source="auto", target=target_lang).translate(text)

    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translates English text into the target language.
        """
        if target_lang in ("en", "english"):
            return text
        elif target_lang == "sheng":
            # English → Swahili → Sheng (approximation)
            text = GoogleTranslator(source="english", target="swahili").translate(text)
            return self._approximate_sheng(text)
        elif target_lang in ("sw", "swahili"):
            return self.translators["en"].translate(text)
        return text

    def _approximate_sheng(self, text: str) -> str:
        """
        Basic approximation of Sheng by replacing common Swahili words.
        """
        replacements = {
            "habari": "niaje",
            "rafiki": "msee",
            "mzuri": "poa",
            "karibu": "form ni gani",
            "asante": "shukz",
            "ndiyo": "ee manze",
        }
        for sw, sh in replacements.items():
            text = text.replace(sw, sh)
        return text


if __name__ == "__main__":
    translator = Translator()

    text = "Niko rada manze, sa kesho fom ni gani"
    detected = translator.detect_language(text)
    print("Detected:", detected)

    translated = translator.translate_to_english(text, detected["language"])
    print("To English:", translated)

    back_translated = translator.translate_from_english("How are you today?", "sw")
    print("Back to Swahili:", back_translated)
