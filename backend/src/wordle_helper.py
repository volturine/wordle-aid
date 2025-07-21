from pathlib import Path
from functools import lru_cache

CURRENT_DIR = Path(__file__).parent


class WordleHelper:
    def __init__(self, length: int = 5):
        self._set_dictionary(length=length)

    def _set_dictionary(self, length: int = 5) -> None:
        with open(f"{CURRENT_DIR.parent}/words_alpha.txt", "r") as file:
            valid_words = set(file.read().split())

        self.dictionary = {word for word in valid_words if len(word) == length}

        # Process the dictionary to create dictionary of characters where for each character there will be up to length lists of words
        self.processed_dictionary = {}
        for word in self.dictionary:
            for pos, char in enumerate(word):
                if char not in self.processed_dictionary:
                    self.processed_dictionary[char] = [set(), set(), set(), set(), set()]
                self.processed_dictionary[char][pos].add(word)

    @lru_cache(maxsize=128)
    def _filter_characters(self, word, incorrect_position: tuple[int], correct_position: tuple[int], incorrect_letter: tuple[int]) -> set[str]:
        filtered = set(word for word in self.dictionary)

        word = word.lower()
        letters_in_incorrect_position = {index: word[index] for index in set(incorrect_position)}
        letters_in_correct_position = {index: word[index] for index in set(correct_position)}
        incorrect_letters = set(
            word[index]
            for index in set(incorrect_letter)
            if word[index] not in (*letters_in_correct_position.values(), *letters_in_incorrect_position.values())
        )

        possible_words = []
        for pos, char in letters_in_correct_position.items():
            possible_words.append(self.processed_dictionary[char][pos])
        filtered = set.intersection(*possible_words, filtered)

        possible_words = []
        for word in filtered:
            masked_word = "".join(char if i not in correct_position else "*" for i, char in enumerate(word))
            if not any(char in masked_word for char in incorrect_letters):
                possible_words.append(word)
        filtered = set(possible_words)

        if letters_in_incorrect_position:
            possible_words = []
            for word in filtered:
                masked_word = "".join(char if i not in correct_position else "*" for i, char in enumerate(word))
                if all((masked_word[pos] != char and char in masked_word) for pos, char in letters_in_incorrect_position.items()):
                    possible_words.append(word)
            filtered = set(possible_words)

        return filtered

    def filter_characters(self, filter_spec: dict[str, dict[str, list[int]]]) -> list[str]:
        filtered = set(word for word in self.dictionary)
        for word, _filter in filter_spec.items():
            filtered = set.intersection(
                filtered,
                self._filter_characters(
                    word, tuple(_filter.get("incorrect_position", ())), tuple(_filter.get("correct_position", ())), tuple(_filter.get("incorrect_letter", ()))
                ),
            )

        return sorted(filtered)


if __name__ == "__main__":
    helper = WordleHelper(5)

    import time

    start_time = time.time()
    filtered = helper.filter_characters(
        {
            "hello": {
                "correct_position": [2],
                "incorrect_letter": [1, 4],
                "incorrect_position": [0, 3],
            },
        },
    )
    end_time = time.time()
    print(f"Filtered words in {end_time - start_time:.4f} seconds:")

    start_time = time.time()
    filtered = helper.filter_characters(
        {
            "hello": {
                "correct_position": [2],
                "incorrect_letter": [1, 4],
                "incorrect_position": [0, 3],
            },
        },
    )
    end_time = time.time()
    print(f"Cached Filtered words in {end_time - start_time:.4f} seconds:")

    print(filtered)
