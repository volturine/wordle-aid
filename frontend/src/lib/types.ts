export enum CharacterState {
    INCORRECT = 'incorrect',
    CORRECT_POSITION = 'correct-position',
    WRONG_POSITION = 'wrong-position'
}

export interface CharacterInfo {
    value: string;
    state: CharacterState;
}

export type WordRow = CharacterInfo[];

export interface FilterSpec {
    [word: string]: {
        correct_position: number[];
        incorrect_letter: number[];
        incorrect_position: number[];
    }
}
