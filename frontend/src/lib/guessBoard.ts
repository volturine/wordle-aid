export interface GuessCell {
	value: string;
	state: string;
}

export interface GuessConstraint {
	guess: string;
	correct_position: number[];
	incorrect_position: number[];
	incorrect_letter: number[];
}

export const MAX_GUESSES = 6;
export const EMPTY_TILE_SENTINEL = '\u200B';
const FULL_BOARD_REASON = 'All six guesses already have letters. Remove a guess to use this word.';

export function tileInputValue(value: string): string {
	return value || EMPTY_TILE_SENTINEL;
}

export function inheritedCellState<T extends GuessCell>(
	rows: T[][],
	rowIndex: number,
	columnIndex: number,
	value: string
): T['state'] {
	if (!value) return 'incorrect' as T['state'];
	for (let r = 0; r < rows.length; r += 1) {
		if (r === rowIndex) continue;
		const cell = rows[r]?.[columnIndex];
		if (cell?.value === value && cell.state === 'correct-position') {
			return 'correct-position' as T['state'];
		}
	}
	return 'incorrect' as T['state'];
}

export function constraintsFromRows(rows: GuessCell[][]): GuessConstraint[] {
	const constraints: GuessConstraint[] = [];
	for (const row of rows) {
		if (row.some((cell) => cell.value && !/^[a-z]$/i.test(cell.value))) {
			throw new Error('Guess cells can only contain letters A to Z');
		}
		const guess = row.map((cell) => cell.value || '_').join('').toLowerCase();
		if (!/^[a-z_]{5}$/.test(guess)) continue;

		const correct_position: number[] = [];
		const incorrect_position: number[] = [];
		const incorrect_letter: number[] = [];
		row.forEach((cell, index) => {
			if (!cell.value) return;
			if (cell.state === 'correct-position') correct_position.push(index);
			else if (cell.state === 'wrong-position') incorrect_position.push(index);
			else incorrect_letter.push(index);
		});
		if (correct_position.length || incorrect_position.length || incorrect_letter.length) {
			constraints.push({ guess, correct_position, incorrect_position, incorrect_letter });
		}
	}
	return constraints;
}

export function placementBlockReason(rows: GuessCell[][]): string {
	const hasEmptyRow = rows.some((row) => row.every((cell) => !cell.value));
	if (hasEmptyRow || rows.length < MAX_GUESSES) return '';
	return FULL_BOARD_REASON;
}

export function placeGuess<T extends GuessCell>(rows: T[][], word: string): {
	rows: T[][];
	placed: boolean;
	focusRow: number;
	reason: string;
} {
	const reason = placementBlockReason(rows);
	if (reason) return { rows, placed: false, focusRow: 0, reason };

	const newRow = word
		.toLowerCase()
		.split('')
		.map((value) => ({ value, state: 'incorrect' as T['state'] })) as T[];
	for (const row of rows) {
		row.forEach((cell, index) => {
			if (cell.value === newRow[index].value && cell.state === 'correct-position') {
				newRow[index].state = 'correct-position' as T['state'];
			}
		});
	}

	const emptyIndex = rows.findIndex((row) => row.every((cell) => !cell.value));
	if (emptyIndex >= 0) {
		const next = rows.slice();
		next[emptyIndex] = newRow;
		return { rows: next, placed: true, focusRow: emptyIndex, reason: '' };
	}
	return { rows: [...rows, newRow], placed: true, focusRow: rows.length, reason: '' };
}

export function backspaceAt(row: GuessCell[], column: number): { focus: number; changed: boolean } {
	if (row[column]?.value || column === 0) return { focus: column, changed: false };
	row[column - 1].value = '';
	row[column - 1].state = 'incorrect';
	return { focus: column - 1, changed: true };
}

export function applyTileInput<T extends GuessCell>(
	rows: T[][],
	rowIndex: number,
	columnIndex: number,
	rawValue: string,
	inputData?: string | null
): {
	kind: 'typed' | 'cleared' | 'backspaced' | 'invalid' | 'noop';
	value: string;
	focusColumn: number;
	invalid: boolean;
} {
	const row = rows[rowIndex];
	const cell = row[columnIndex];
	const previousValue = cell.value;
	const stripped = rawValue.replace(/\u200B/g, '');

	if (!stripped) {
		if (previousValue) {
			cell.value = '';
			cell.state = 'incorrect' as T['state'];
			return { kind: 'cleared', value: '', focusColumn: columnIndex, invalid: false };
		}
		const applied = backspaceAt(row, columnIndex);
		return {
			kind: applied.changed ? 'backspaced' : 'noop',
			value: '',
			focusColumn: applied.focus,
			invalid: false
		};
	}

	const cleanData = (inputData ?? '').replace(/\u200B/g, '');
	let typed = '';
	if (cleanData.length > 0) {
		typed = cleanData.at(-1) ?? '';
	} else if (previousValue && stripped.length > 1) {
		if (stripped.toLowerCase().startsWith(previousValue.toLowerCase())) {
			typed = stripped.slice(previousValue.length).at(-1) ?? '';
		} else {
			typed = stripped[0] ?? '';
		}
	} else {
		typed = stripped.at(-1) ?? '';
	}

	if (!/^[a-z]$/i.test(typed)) {
		cell.value = '';
		cell.state = 'incorrect' as T['state'];
		return { kind: 'invalid', value: '', focusColumn: columnIndex, invalid: true };
	}

	const value = typed.toLowerCase();
	cell.value = value;
	cell.state = inheritedCellState(rows, rowIndex, columnIndex, value);
	return {
		kind: 'typed',
		value,
		focusColumn: columnIndex < 4 ? columnIndex + 1 : columnIndex,
		invalid: false
	};
}
