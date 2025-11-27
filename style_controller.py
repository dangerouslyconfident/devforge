import re

class StyleController:
    def __init__(self):
        self.formal_replacements = {
            r"\bcan't\b": "cannot",
            r"\bwon't\b": "will not",
            r"\bI'm\b": "I am",
            r"\bit's\b": "it is",
            r"\bgonna\b": "going to",
            r"\bwanna\b": "want to",
            r"\bgotta\b": "have to",
            r"\bkids\b": "children",
            r"\bthanks\b": "thank you",
            r"\bhi\b": "hello",
            r"\bguys\b": "everyone"
        }
        
        self.concise_removals = [
            r"\breally\b", r"\bvery\b", r"\bjust\b", r"\bactually\b", 
            r"\bbasically\b", r"\bliterally\b", r"\bquite\b", r"\bsomewhat\b"
        ]

    def apply_style(self, text, style="Neutral"):
        if style == "Formal":
            return self._make_formal(text)
        elif style == "Casual":
            return self._make_casual(text)
        elif style == "Concise":
            return self._make_concise(text)
        else:
            return text

    def _make_formal(self, text):
        for pattern, replacement in self.formal_replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _make_casual(self, text):
        # For now, just return as is or maybe add some contractions if we had a reverse map
        # Casual is often the default speech pattern
        return text

    def _make_concise(self, text):
        for word in self.concise_removals:
            text = re.sub(word, "", text, flags=re.IGNORECASE)
        # Clean up double spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

if __name__ == "__main__":
    sc = StyleController()
    sample = "I'm really gonna go to the store, thanks guys."
    print(f"Original: {sample}")
    print(f"Formal: {sc.apply_style(sample, 'Formal')}")
    print(f"Concise: {sc.apply_style(sample, 'Concise')}")
