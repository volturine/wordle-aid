import assert from 'node:assert/strict';
import test from 'node:test';
import { paginationItems } from './pagination.ts';

test('short lists show every page number', () => {
	assert.deepEqual(paginationItems(1, 1), [1]);
	assert.deepEqual(paginationItems(2, 3), [1, 2, 3]);
});

test('long lists keep the ends and a window around the current page', () => {
	assert.deepEqual(paginationItems(1, 12), [1, 2, 3, 4, 5, 'gap', 12]);
	assert.deepEqual(paginationItems(6, 12), [1, 'gap', 4, 5, 6, 7, 8, 'gap', 12]);
	assert.deepEqual(paginationItems(12, 12), [1, 'gap', 8, 9, 10, 11, 12]);
});
