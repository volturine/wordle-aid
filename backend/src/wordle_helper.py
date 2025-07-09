from pathlib import Path

CURRENT_DIR = Path(__file__).parent


class WordleHelper:
    def __init__(self, length: int = 5):
        self._set_dictionary(length=length)

    def _set_dictionary(self, length: int = 5) -> set[str]:
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

    def filter_characters(self, filter_spec: list[dict[str]]) -> None:
        filtered = set(word for word in self.dictionary)
        for word, _filter in filter_spec.items():
            word = word.lower()
            letters_in_incorrect_position = {index: word[index] for index in set(_filter.get("incorrect_position", []))}
            letters_in_correct_position = {index: word[index] for index in set(_filter.get("correct_position", []))}
            incorrect_letters = set(
                word[index]
                for index in set(_filter.get("incorrect_letter", []))
                if word[index] not in (*letters_in_correct_position.values(), *letters_in_incorrect_position.values())
            )

            possible_words = []
            for pos, char in letters_in_correct_position.items():
                possible_words.append(self.processed_dictionary[char][pos])
            filtered = set.intersection(*possible_words, filtered)

            possible_words = []
            for word in filtered:
                masked_word = "".join(char if i not in _filter["correct_position"] else "*" for i, char in enumerate(word))
                if not any(char in masked_word for char in incorrect_letters):
                    possible_words.append(word)
            filtered = set(possible_words)

            if letters_in_incorrect_position:
                possible_words = []
                for word in filtered:
                    masked_word = "".join(char if i not in _filter["correct_position"] else "*" for i, char in enumerate(word))
                    if all((masked_word[pos] != char and char in masked_word) for pos, char in letters_in_incorrect_position.items()):
                        possible_words.append(word)
                filtered = set(possible_words)

        return sorted(filtered)


if __name__ == "__main__":
    helper = WordleHelper(5)

    filtered = helper.filter_characters(
        {
            "hello": {
                "correct_position": [2],
                "incorrect_letter": [1, 2, 4],
                "incorrect_position": [0, 3],
            },
        },
    )

    print(filtered)
