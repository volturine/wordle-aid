export enum CharacterState {
    WRITING = 'writing',
    INCORRECT = 'incorrect',
    WRONG_POSITION = 'wrong-position',
    CORRECT_POSITION = 'correct-position',
}

export interface CharacterInfo {
    value: string;
    state: CharacterState;
}


export interface DictionaryMeaning {
    partOfSpeech: string;
    definition: string;
}

export interface DictionaryEntry {
    word: string;
    meanings: DictionaryMeaning[];
}
