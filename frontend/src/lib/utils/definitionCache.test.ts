import assert from 'node:assert/strict';
import test from 'node:test';
import { pruneDefinitionCache } from './definitionCache.ts';

test('prune drops expired entries and the oldest extras', () => {
	const now = 1_000_000;
	const cache: Record<string, { data: { word: string; definitions: [] }; timestamp: number }> = {};
	cache.old = { data: { word: 'old', definitions: [] }, timestamp: now - 8 * 24 * 60 * 60 * 1000 };
	for (let index = 0; index < 201; index += 1) {
		cache[`w${index}`] = { data: { word: `w${index}`, definitions: [] }, timestamp: now - 201 + index };
	}
	const pruned = pruneDefinitionCache(cache, now);
	assert.equal(pruned.old, undefined);
	assert.equal(Object.keys(pruned).length, 200);
	assert.equal(pruned.w0, undefined);
	assert.ok(pruned.w200);
});
