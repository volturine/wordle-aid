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

test('an empty definition expires after 15 minutes and a real one lasts seven days', () => {
	const now = 1_000_000;
	const minute = 60 * 1000;
	const day = 24 * 60 * minute;
	const cache = {
		miss: { data: { word: 'miss', definitions: [] }, timestamp: now - 16 * minute },
		freshMiss: { data: { word: 'fresh', definitions: [] }, timestamp: now - 14 * minute },
		hit: {
			data: { word: 'hit', definitions: [{ partOfSpeech: 'noun', definition: 'a bird' }] },
			timestamp: now - 2 * day
		},
		staleHit: {
			data: { word: 'stale', definitions: [{ partOfSpeech: 'noun', definition: 'old' }] },
			timestamp: now - 8 * day
		}
	};
	const pruned = pruneDefinitionCache(cache, now);
	assert.equal(pruned.miss, undefined);
	assert.ok(pruned.freshMiss);
	assert.ok(pruned.hit);
	assert.equal(pruned.staleHit, undefined);
});
