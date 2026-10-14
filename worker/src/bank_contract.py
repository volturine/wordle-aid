"""Checks that a loaded dictionary is the reviewed guess and answer bank."""

REQUIRED_ANSWERS = (
    'detox',
    'geeky',
    'inbox',
    'latte',
    'penne',
    'pesto',
    'ramen',
    'rehab',
    'wimpy',
)
FORBIDDEN_GUESSES = ('aaron', 'abbie', 'abdom', 'accel', 'accts')
MIN_GUESSES = 14000
MIN_ANSWERS = 4000


def bank_problem(words: set[str], answers: set[str], guess_count: int, answer_count: int) -> str | None:
    """Return a reason the bank cannot serve traffic, or None when it can."""
    if not answers <= words:
        return 'likely answers are not all accepted guesses'
    if len(words) < MIN_GUESSES or guess_count != len(words):
        return 'guess bank is missing or does not match its metadata'
    if len(answers) < MIN_ANSWERS or answer_count != len(answers):
        return 'answer bank is missing or does not match its metadata'
    if any(word not in answers for word in REQUIRED_ANSWERS):
        return 'required answers are missing'
    if any(word in words for word in FORBIDDEN_GUESSES):
        return 'retired dictionary words are still loaded'
    return None
