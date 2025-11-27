import unittest
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_cleaner import TextCleaner
from style_controller import StyleController
# GrammarCorrector requires loading model, might be slow for unit test, but let's try if installed

class TestModules(unittest.TestCase):
    def setUp(self):
        self.cleaner = TextCleaner()
        self.style = StyleController()

    def test_cleaner_disfluency(self):
        text = "Umm, I want to, like, go."
        cleaned = self.cleaner.remove_disfluencies(text)
        self.assertEqual(cleaned, "I want to, go.")

    def test_cleaner_repetition(self):
        text = "I want to go to the the store."
        cleaned = self.cleaner.remove_repetitions(text)
        self.assertEqual(cleaned, "I want to go to the store.")

    def test_style_formal(self):
        text = "I can't go."
        styled = self.style.apply_style(text, "Formal")
        self.assertEqual(styled, "I cannot go.")

    def test_style_concise(self):
        text = "I am really very happy."
        styled = self.style.apply_style(text, "Concise")
        self.assertEqual(styled, "I am happy.")

if __name__ == "__main__":
    unittest.main()
