import re

class TextCleaner:
    def __init__(self):
        # Common fillers to remove
        self.fillers = [
            r"\bumm\b", r"\buhh\b", r"\bum\b", r"\buh\b", 
            r"\blike\b", r"\byou know\b", r"\bI mean\b", r"\bsort of\b"
        ]
        self.filler_pattern = re.compile("|".join(self.fillers), re.IGNORECASE)

    def remove_disfluencies(self, text):
        """Removes filler words."""
        cleaned_text = self.filler_pattern.sub("", text)
        # Clean up extra spaces
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        # Clean up repeated punctuation (e.g. ", ,")
        cleaned_text = re.sub(r"\s*,\s*,", ",", cleaned_text)
        # Clean up leading/trailing punctuation if fillers were at start/end
        cleaned_text = cleaned_text.strip(", ")
        return cleaned_text

    def remove_repetitions(self, text):
        """Removes adjacent duplicate words (e.g., 'the the')."""
        # Pattern to find repeated words
        # \b(\w+)\b matches a word
        # \s+ matches whitespace
        # \1 matches the same word again
        pattern = re.compile(r"\b(\w+)\b\s+\1\b", re.IGNORECASE)
        
        # Apply repeatedly until no more duplicates found
        while True:
            new_text = pattern.sub(r"\1", text)
            if new_text == text:
                break
            text = new_text
            
        return text

    def clean(self, text):
        text = self.remove_disfluencies(text)
        text = self.remove_repetitions(text)
        return text

if __name__ == "__main__":
    cleaner = TextCleaner()
    sample = "Umm, I want to, like, go to the the store."
    print(f"Original: {sample}")
    print(f"Cleaned: {cleaner.clean(sample)}")
