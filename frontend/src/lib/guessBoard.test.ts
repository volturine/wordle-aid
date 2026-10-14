import assert from 'node:assert/strict';
import test from 'node:test';
import { backspaceAt, constraintsFromRows, placeGuess, type GuessCell } from './guessBoard.ts';

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
