//
import type { CharacterInfo, DictionaryEntry } from './interfaces';

export type WordRow = CharacterInfo[];
export type DictionaryResponse = DictionaryEntry;
export interface FilterSpec {
    [word: string]: {
        correct_position: number[];
        incorrect_letter: number[];
        incorrect_position: number[];
    }
}