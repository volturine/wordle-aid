//
import type { CharacterInfo, DictionaryEntry } from './interfaces';

export type WordRow = CharacterInfo[];
export type DictionaryResponse = DictionaryEntry;

export interface FilterResponse {
	answers: string[];
	guesses: string[];
	answer_total: number;
	guess_total: number;
	answer_offset: number;
	guess_offset: number;
	limit: number;
	needs_clue: boolean;
	bank_version: string;
}