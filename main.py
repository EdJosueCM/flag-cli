import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "countries.json"
BEST_PATH = BASE_DIR / "best_score.json"

PALETTE = {
    "red": 196,
    "blue": 21,
    "green": 28,
    "white": 15,
    "black": 0,
    "yellow": 226,
    "gold": 220,
    "orange": 208,
    "sky": 45,
}

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

CLEAR = "\033[2J\033[H"

FONT = {
    "F": ["XXXXX", "X....", "XXXX.", "X....", "X...."],
    "L": ["X....", "X....", "X....", "X....", "XXXXX"],
    "A": [".XXX.", "X...X", "XXXXX", "X...X", "X...X"],
    "G": [".XXXX", "X....", "X..XX", "X...X", ".XXX."],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "XXXX."],
    "E": ["XXXXX", "X....", "XXXX.", "X....", "XXXXX"],
    "X": ["X...X", ".X.X.", "..X..", ".X.X.", "X...X"],
}
TITLE = "FLAGDEX"
TITLE_COLORS = ["red", "orange", "yellow", "green", "sky", "blue", "white"]

TOTAL_ROUNDS = 10
MAX_ATTEMPTS = 3


def load_countries():
    with open(DATA_PATH, encoding="utf-8") as file:
        return json.load(file)


def load_best():
    try:
        with open(BEST_PATH, encoding="utf-8") as file:
            return json.load(file)["best"]
    except (OSError, ValueError, KeyError):
        return 0


def save_best(percent):
    with open(BEST_PATH, "w", encoding="utf-8") as file:
        json.dump({"best": percent}, file)


def flag_emoji(code):
    return "".join(chr(0x1F1E6 + ord(letter) - ord("A")) for letter in code.upper())


def draw_flag(country, mode="blocks"):
    if mode == "emoji":
        print(flag_emoji(country["code"]))
        return
    for row in country["pattern"]:
        line = ""
        for color in row:
            line += f"\x1b[48;5;{PALETTE[color]}m  "
        line += RESET
        print(line)


def draw_title():
    for row in range(5):
        line = ""
        for letter, color in zip(TITLE, TITLE_COLORS):
            for cell in FONT[letter][row]:
                if cell == "X":
                    line += f"\x1b[48;5;{PALETTE[color]}m  {RESET}"
                else:
                    line += "  "
            line += " "
        print(line)


def clear_screen():
    print(CLEAR, end="")


def normalize(text):
    return " ".join(text.lower().split())


def is_correct(guess, country):
    valid = [country["name"]] + country.get("aliases", [])
    return normalize(guess) in [normalize(name) for name in valid]


def ask_choice(prompt, options):
    while True:
        answer = input(prompt).strip().lower()
        if answer in options:
            return answer
        print(f"Please type one of: {', '.join(options)}")


def play_round(country, difficulty, mode="blocks"):
    if difficulty == "easy":
        print(f"Hint: it's in {country['continent']}.")

    draw_flag(country, mode)

    attempts = 0
    while attempts < MAX_ATTEMPTS:
        guess = input("What country is this? ")
        if is_correct(guess, country):
            print(f"{GREEN}Correct!{RESET}")
            return 1

        attempts += 1
        remaining = MAX_ATTEMPTS - attempts
        if remaining > 0:
            print(f"Nope, try again ({remaining} attempts left)")

    print(f"{RED}It was {country['name']}.{RESET}")
    return 0


def rating(percent):
    if percent == 100:
        return "Perfect!"
    if percent >= 80:
        return "Great job!"
    if percent >= 50:
        return "Not bad."
    return "Keep practicing!"


def play_game(countries):
    clear_screen()
    draw_title()
    print()
    difficulty = ask_choice("Difficulty (easy/hard)? ", ("easy", "hard"))
    mode = ask_choice("Show flags as (blocks/emoji)? ", ("blocks", "emoji"))

    rounds = random.sample(countries, min(TOTAL_ROUNDS, len(countries)))

    score = 0
    for number, country in enumerate(rounds, start=1):
        print(f"\n--- Round {number} of {len(rounds)} ---")
        score += play_round(country, difficulty, mode)

    print("\n=== Game over ===")
    print(f"Score: {score}/{len(rounds)}")
    percent = round(100 * score / len(rounds))
    print(rating(percent))

    best = load_best()
    if percent > best:
        save_best(percent)
        print(f"New best score: {percent}%!")
    else:
        print(f"Best score: {best}%")


def main():
    countries = load_countries()
    try:
        while True:
            play_game(countries)
            if ask_choice("\nPlay again (yes/no)? ", ("yes", "no")) == "no":
                break
    except (KeyboardInterrupt, EOFError):
        print(f"{RESET}\nBye!")


if __name__ == "__main__":
    main()
