import type { WordRow, DictionaryResponse, FilterSpec } from './types';
import { CharacterState } from './interfaces';
import { API_BASE } from './config';

function convertWordRowToFilterSpec(rows: WordRow[]): FilterSpec {
    const filter_spec: FilterSpec = {};

    for (const row of rows) {
        const word = row.map(c => c.value || '_').join('');
        if (!/^[a-zA-Z_]{5}$/.test(word)) continue;

        const correct_position: number[] = [];
        const incorrect_letter: number[] = [];
        const incorrect_position: number[] = [];

        row.forEach((c, idx) => {
            if (!c.value) return;
            if (c.state === CharacterState.CORRECT_POSITION) {
                correct_position.push(idx);
            } else if (c.state === CharacterState.WRONG_POSITION) {
                incorrect_position.push(idx);
            } else {
                incorrect_letter.push(idx);
            }
        });

        if (correct_position.length || incorrect_letter.length || incorrect_position.length) {
            filter_spec[word] = {
                correct_position,
                incorrect_letter,
                incorrect_position
            };
        }
    }

    return filter_spec;
}

export async function filterWords(rows: WordRow[]): Promise<string[]> {
    const filter_spec = convertWordRowToFilterSpec(rows);
    const res = await fetch(`${API_BASE}/filter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filter_spec })
    });

    if (!res.ok) {
        throw new Error('Failed to filter words');
    }

    return res.json();
}

export async function getWordDefinition(word: string): Promise<DictionaryResponse> {
    const res = await fetch(`${API_BASE}/word-definition/${word}`);

    if (!res.ok) {
        throw new Error('Failed to fetch word definition');
    }

    return res.json();
}
