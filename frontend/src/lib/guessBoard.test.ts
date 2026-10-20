import assert from 'node:assert/strict';
import test from 'node:test';
import {
	EMPTY_TILE_SENTINEL,
	applyTileInput,
	backspaceAt,
	constraintsFromRows,
	placeGuess,
	tileInputValue,
	type GuessCell
} from './guessBoard.ts';

const row = (letters: string, states: string[] = []): GuessCell[] =>
	letters.split('').map((value, index) => ({
		value: value === '_' ? '' : value,
		state: states[index] ?? 'incorrect'
	}));

test('duplicate guess rows both become constraints', () => {
	const constraints = constraintsFromRows([
		row('crane', ['correct-position', 'incorrect', 'incorrect', 'incorrect', 'incorrect']),
		row('crane', ['incorrect', 'wrong-position', 'incorrect', 'incorrect', 'incorrect'])
	]);
	assert.equal(constraints.length, 2);
	assert.deepEqual(constraints[0].correct_position, [0]);
	assert.deepEqual(constraints[1].incorrect_position, [1]);
});

test('a partial row keeps its filled squares', () => {
	const constraints = constraintsFromRows([row('c____', ['correct-position'])]);
	assert.equal(constraints[0].guess, 'c____');
	assert.deepEqual(constraints[0].correct_position, [0]);
});

test('backspace in an empty square changes the previous letter', () => {
	const cells = row('ab___');
	const result = backspaceAt(cells, 2);
	assert.equal(result.changed, true);
	assert.equal(result.focus, 1);
	assert.equal(cells[1].value, '');
});

test('android IME backspace on an empty sentinel square deletes the previous letter', () => {
	const rows = [row('cabi_')];
	const result = applyTileInput(rows, 0, 4, '', null);
	assert.equal(result.kind, 'backspaced');
	assert.equal(result.focusColumn, 3);
	assert.equal(rows[0][3].value, '');
	assert.equal(tileInputValue(rows[0][4].value), EMPTY_TILE_SENTINEL);
});

test('typing a new letter into a filled square overwrites the existing letter and resets stale color', () => {
	const rows = [row('crane', ['correct-position', 'wrong-position'])];
	const result = applyTileInput(rows, 0, 1, 'rt', 't');
	assert.equal(result.kind, 'typed');
	assert.equal(rows[0][1].value, 't');
	assert.equal(rows[0][1].state, 'incorrect');
	assert.equal(result.focusColumn, 2);
});

test('typing a letter that matches an earlier green column inherits correct-position', () => {
	const rows = [row('crane', ['correct-position']), row('_____')];
	const result = applyTileInput(rows, 1, 0, `${EMPTY_TILE_SENTINEL}c`, 'c');
	assert.equal(result.kind, 'typed');
	assert.equal(rows[1][0].value, 'c');
	assert.equal(rows[1][0].state, 'correct-position');
	assert.equal(result.focusColumn, 1);
});

test('use guess on a full board does not replace a row', () => {
	const rows = Array.from({ length: 6 }, () => row('a____'));
	const placed = placeGuess(rows, 'crane');
	assert.equal(placed.placed, false);
	assert.equal(placed.rows, rows);
	assert.match(placed.reason, /six guesses/);
});

test('use guess fills an empty row before adding one', () => {
	const rows = [row('a____'), row('_____')];
	const placed = placeGuess(rows, 'crane');
	assert.equal(placed.placed, true);
	assert.equal(placed.focusRow, 1);
	assert.equal(placed.rows[1].map((cell) => cell.value).join(''), 'crane');
	assert.equal(rows[1][0].value, '');
});
