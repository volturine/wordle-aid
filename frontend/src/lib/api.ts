import type { WordRow, DictionaryResponse, FilterResponse } from './types';
import { constraintsFromRows } from './guessBoard';
import { API_BASE } from './config';

export const FILTER_PAGE_SIZE = 100;

export async function filterWords(
	rows: WordRow[],
	options: { answerOffset?: number; guessOffset?: number; signal?: AbortSignal } = {}
): Promise<FilterResponse> {
	const res = await fetch(`${API_BASE}/filter/five_letter_words`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			constraints: constraintsFromRows(rows),
			limit: FILTER_PAGE_SIZE,
			answer_offset: options.answerOffset ?? 0,
			guess_offset: options.guessOffset ?? 0
		}),
		signal: options.signal
	});

	if (!res.ok) {
		let detail = res.status === 503 ? 'Word bank is unavailable. Try again shortly.' : 'Failed to filter words';
		try {
			const body = await res.json();
			if (typeof body?.detail === 'string') detail = body.detail;
		} catch {
			// Keep the fallback message when the server did not return JSON.
		}
		throw new Error(detail);
	}

	return res.json();
}

export async function getWordDefinition(word: string, signal?: AbortSignal): Promise<DictionaryResponse> {
	const res = await fetch(`${API_BASE}/word-definition/${word}`, { signal });

	if (!res.ok) {
		throw new Error('Failed to fetch word definition');
	}

	return res.json();
}
