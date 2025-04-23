from googletrans import Translator

class TranslationService:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text, source_lang="auto", target_lang="zh-cn"):
        try:
            translated = self.translator.translate(text, src=source_lang, dest=target_lang)
            return translated.text
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")