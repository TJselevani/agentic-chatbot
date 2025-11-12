from deep_translator import GoogleTranslator

class Translator:
    def __init__(self):
        self.translators = {
            "swahili": GoogleTranslator(source="swahili", target="english"),
            "english": GoogleTranslator(source="english", target="swahili"),
        }

    def translate_to_english(self, text: str, source_lang: str) -> str:
        if source_lang == "english":
            return text
        elif source_lang == "sheng":
            # Sheng → Swahili → English (approximation)
            text = GoogleTranslator(source="auto", target="swahili").translate(text)
            return GoogleTranslator(source="swahili", target="english").translate(text)
        elif source_lang == "swahili":
            return self.translators["swahili"].translate(text)
        return text

    def translate_from_english(self, text: str, target_lang: str) -> str:
        if target_lang == "english":
            return text
        elif target_lang == "sheng":
            # English → Swahili → Sheng (approximation)
            text = GoogleTranslator(source="english", target="swahili").translate(text)
            return self._approximate_sheng(text)
        elif target_lang == "swahili":
            return self.translators["english"].translate(text)
        return text

    def _approximate_sheng(self, text: str) -> str:
        """
        Basic approximation of Sheng by replacing common Swahili words.
        You can expand this lexicon later.
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
