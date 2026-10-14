//
import type { CharacterInfo, DictionaryEntry } from './interfaces';

export type WordRow = CharacterInfo[];
export type DictionaryResponse = DictionaryEntry;

export interface FilterResponse {
	words: string[];
	total: number;
	offset: number;
	limit: number;
	needs_clue: boolean;
	bank_version: string;
}