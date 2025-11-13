from transformers import MarianMTModel, MarianTokenizer

tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-swa-en")
model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-swa-en")


def translate_to_english(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)


if "__main__" == __name__:
    text = "Niko rada manze, sa kesho fom ni gani"
    response = translate_to_english(text)
    print(response)

