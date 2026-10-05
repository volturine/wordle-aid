# Wordle Aid Design System

## Direction

Wordle Aid is a quiet puzzle desk: clear, friendly, and focused on the five-letter board. Use a warm paper surface, ink-like text, and familiar Wordle feedback colors as restrained accents. Keep the board and the Filter action visually prominent; supporting instructions and definitions stay calm.

## Color

Use semantic tokens from `frontend/src/app.css` rather than component-specific color literals.

| Token              | Light     | Dark      | Use                                                              |
| ------------------ | --------- | --------- | ---------------------------------------------------------------- |
| `--page`           | `#f5f4ef` | `#171a18` | Page background                                                  |
| `--surface`        | `#fffefa` | `#232825` | Main panel                                                       |
| `--surface-raised` | `#ffffff` | `#2b312d` | Inputs and popovers                                              |
| `--ink`            | `#202521` | `#f2f3ef` | Main text                                                        |
| `--muted`          | `#59635c` | `#b9c2bb` | Help text and secondary labels                                   |
| `--line`           | `#d6dbd5` | `#4a554d` | Borders and separators                                           |
| `--line-strong`    | `#87918a` | `#849087` | Interactive borders and selected controls                        |
| `--green`          | `#376a34` | `#6aaa64` | Primary action; white text in light mode, `#172018` in dark mode |
| `--green-hover`    | `#2d572b` | `#83bd7d` | Primary action hover                                             |
| `--tile-green`     | `#6aaa64` | `#6aaa64` | Correct position, paired with `--tile-ink`                       |
| `--yellow`         | `#c9b458` | `#c9b458` | Wrong position, paired with `--tile-ink`                         |
| `--gray`           | `#8a928b` | `#8a928b` | Incorrect letters, paired with `--tile-ink`                      |
| `--tile-ink`       | `#172018` | `#172018` | Text on feedback tiles                                           |
| `--danger`         | `#b42318` | `#ff8b82` | Errors and destructive actions                                   |
| `--danger-surface` | `#fff1ef` | `#3c2421` | Error and destructive control surface                            |
| `--action-ink`     | `#ffffff` | `#172018` | Text on the primary action                                       |
| `--focus`          | `#215fa8` | `#94c5ff` | Keyboard focus ring                                              |
| `--shadow`         | `0 10px 30px rgb(30 39 32 / 8%)` | `0 12px 34px rgb(0 0 0 / 24%)` | Main card and popover depth |

`--tile-ink` is `#172018` in both themes. Text and icons must keep at least 4.5:1 contrast for normal text. Large tile letters and meaningful non-text control boundaries must keep at least 3:1. Choose foreground tokens for each state; never assume white or ink works on every feedback color.

## Typography

Use the system UI sans-serif stack for readable, portable text. Board letters use a bold system monospace stack. Controls inherit the interface font.

| Role              | Size / line height | Weight  |
| ----------------- | ------------------ | ------- |
| Page title        | `2rem / 1.15`      | 700     |
| Section title     | `1.25rem / 1.3`    | 650     |
| Body and controls | `1rem / 1.5`       | 400–600 |
| Supporting text   | `0.875rem / 1.45`  | 400     |
| Board letters     | `1.5rem / 1`       | 700     |

Use `rem` for type sizing so browser text enlargement remains effective.

## Spacing and shape

Use the four-pixel spacing scale: `4`, `8`, `12`, `16`, `24`, `32`, and `48` pixels. Use `8px` for controls and inputs, `16px` for cards, and `32px` for large panels. Keep repeated controls on the same spacing and radius tokens.

Use `8px` for control corners, `16px` for cards, and a pill radius only for compact label badges. Borders are `1px` structural lines; letter tiles keep a `2px` border in both empty and colored states. Keyboard focus uses a `3px` ring with a `3px` offset.

Interactive targets are at least `44px` square. Inputs and buttons use `border-box`. The main content width is at most `48rem`. At `520px` and below the card becomes full-bleed (no border, radius, or shadow) with `16px` side padding, and the brand and theme button share one top bar above a full-width heading. The mobile heading uses `1.75rem`; other sizes remain at their role sizes. No component may require horizontal page scrolling.

The guess board is a centered column of at most `20rem` with five equal tiles; empty tiles use the neutral surface style and only lettered tiles show feedback colors. The row remove button is a borderless trailing icon and appears only when more than one guess exists. The board reserves an equal empty column on both sides of the tiles (`44px`, or `36px` at `520px` and below), so the tiles stay centered and never move when a guess is added or removed. Desktop reserves scrollbar space; at `520px` and below the page scrollbar is hidden, as on phones.

The color guide shows three columns on wide screens and stacks into aligned rows (swatch, name, meaning) at `520px` and below so no meaning wraps. The entry mode toggle is a two-segment control, and the secondary actions split the row in equal halves.

## Interaction

- Every control has a visible keyboard focus ring, hover feedback where hover exists, pressed feedback, and a distinct disabled state.
- Loading, success, empty, validation, and request failure states remain visible and are announced through status or alert semantics.
- Feedback is communicated with both color and accessible text.
- Popovers identify themselves, receive focus when opened, close with Escape, and return focus to their trigger.
- Motion is limited to `160ms` state transitions and respects `prefers-reduced-motion`.
