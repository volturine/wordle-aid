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


export interface DictionaryDefinition {
    definition: string;
    example?: string;
    synonyms: string[];
    antonyms: string[];
}

export interface DictionaryMeaning {
    partOfSpeech: string;
    definitions: DictionaryDefinition[];
}

export interface DictionaryPhonetic {
    text: string;
    audio?: string;
}

export interface DictionaryEntry {
    word: string;
    phonetic?: string;
    phonetics: DictionaryPhonetic[];
    origin?: string;
    meanings: DictionaryMeaning[];
}
