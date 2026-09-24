import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent))
import main


class NormalizeTests(unittest.TestCase):
    def test_lowercases_and_collapses_spaces(self):
        self.assertEqual(main.normalize("  United   STATES "), "united states")


class DataTests(unittest.TestCase):
    def test_every_country_is_valid(self):
        for country in main.load_countries():
            self.assertEqual(len(country["pattern"]), 5, country["name"])
            for row in country["pattern"]:
                self.assertEqual(len(row), 8, country["name"])
                for color in row:
                    self.assertIn(color, main.PALETTE, country["name"])

    def test_names_and_codes_are_unique(self):
        countries = main.load_countries()
        self.assertEqual(len({c["name"] for c in countries}), len(countries))
        self.assertEqual(len({c["code"] for c in countries}), len(countries))


class AnswerTests(unittest.TestCase):
    def test_alias_is_accepted(self):
        us = {"name": "United States", "aliases": ["usa"]}
        self.assertTrue(main.is_correct(" USA ", us))
        self.assertFalse(main.is_correct("canada", us))

    def test_flag_emoji(self):
        self.assertEqual(main.flag_emoji("FR"), "\U0001F1EB\U0001F1F7")


class PlayRoundTests(unittest.TestCase):
    country = {"name": "France", "code": "FR", "continent": "Europe",
               "pattern": [["red"] * 8] * 5}

    def run_round(self, answers, difficulty="hard"):
        out = io.StringIO()
        with mock.patch("builtins.input", side_effect=answers), redirect_stdout(out):
            result = main.play_round(self.country, difficulty)
        return result, out.getvalue()

    def test_correct_first_try(self):
        self.assertEqual(self.run_round(["france"])[0], 1)

    def test_correct_on_last_attempt(self):
        self.assertEqual(self.run_round(["a", "b", "France"])[0], 1)

    def test_three_misses_reveal_answer(self):
        result, output = self.run_round(["a", "b", "c"])
        self.assertEqual(result, 0)
        self.assertIn("It was France.", output)

    def test_easy_shows_hint(self):
        self.assertIn("Europe", self.run_round(["france"], "easy")[1])


class TitleTests(unittest.TestCase):
    def test_title_is_five_rows_and_every_letter_is_5x5(self):
        for letter, rows in main.FONT.items():
            self.assertEqual(len(rows), 5, letter)
            self.assertTrue(all(len(r) == 5 for r in rows), letter)
        out = io.StringIO()
        with redirect_stdout(out):
            main.draw_title()
        self.assertEqual(len(out.getvalue().splitlines()), 5)


class AskChoiceTests(unittest.TestCase):
    def test_reprompts_until_valid(self):
        with mock.patch("builtins.input", side_effect=["", "medium", " HARD "]), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(main.ask_choice("? ", ("easy", "hard")), "hard")


if __name__ == "__main__":
    unittest.main()
