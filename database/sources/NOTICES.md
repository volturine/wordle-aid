# Word bank notices

Wordle Aid ships two lists:

- **Accepted guesses** are the words a Wordle-style game can accept.
- **Likely answers** are the smaller set shown first. Every likely answer is also an accepted guess.

The previous SQLite dictionary is not part of either list. Unioning it back in would keep entries such as `aaron`, `abbie`, `abdom`, `accel`, and `accts`.

## tabatkins/wordle-list

Accepted guesses come from [tabatkins/wordle-list](https://github.com/tabatkins/wordle-list), commit `255b9469c4dad99a3b95cc4ddbe139b3d3747868` (2022-09-06, “Re-shuffle”), retrieved 2026-10-14.

That repository is MIT licensed. Copyright (c) 2022 Tab Atkins Jr. The license text is in `tabatkins-LICENSE`. The upstream README describes the file as possible valid guesses taken from the game’s source, not as a live or complete answer schedule.

SHA-256 of `tabatkins-wordle-list.txt`: `9df5dad1b44cf1b9e0fa7c3ebff94d69ff7efb59f8691ac88e74e1c7b3da121e`

## 12dicts 3of6game

Likely answers start as the five-letter words in Alan Beale’s 12dicts `3of6game` list, release 6.0.2 (June 2016), that also appear in the guess list. 12dicts is oriented toward common English and this list includes inflections used by word games. Alan Beale released the 12dicts lists to the public domain and asked for acknowledgment of their use. The `2of12inf` and `2+2+3` lists were not used, because their readme says the AGID dependency keeps them out of the public domain.

Source: <https://wordlist.aspell.net/12dicts/> and `12dicts-6.0.2.zip`.

SHA-256 of `12dicts-3of6game.txt`: `ad7b041b98e09a30ae9f4938ac24ca919a434b021a6b8582a69ad5d4863dabf0`

## Supplement

`answer-supplement.txt` forces nine words into the likely-answer set when they are already accepted guesses: detox, geeky, inbox, latte, penne, pesto, ramen, rehab, and wimpy. Measured against 3of6game, only `penne` and `ramen` were outside that common list. The nine words are the historical answers the old bank could not return. They are not a redistribution of the New York Times answer list.

No list here is an official or current New York Times Wordle answer feed.
