import assert from 'node:assert/strict';
import test from 'node:test';
import { readStorage, removeStorage, writeStorage } from './storage.ts';

function brokenStore() {
	return {
		getItem() {
			throw new Error('disabled');
		},
		setItem() {
			throw new Error('full');
		},
		removeItem() {
			throw new Error('disabled');
		}
	};
}

test('storage failures stay in memory', () => {
	const store = brokenStore();
	assert.equal(readStorage('theme', store), null);
	assert.doesNotThrow(() => writeStorage('theme', 'dark', store));
	assert.doesNotThrow(() => removeStorage('theme', store));
});

test('storage round-trips through a working store', () => {
	const values = new Map<string, string>();
	const store = {
		getItem: (key: string) => values.get(key) ?? null,
		setItem: (key: string, value: string) => values.set(key, value),
		removeItem: (key: string) => values.delete(key)
	};
	writeStorage('board', '[]', store);
	assert.equal(readStorage('board', store), '[]');
	removeStorage('board', store);
	assert.equal(readStorage('board', store), null);
});
