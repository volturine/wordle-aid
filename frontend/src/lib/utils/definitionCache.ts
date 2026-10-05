import type { DictionaryResponse } from '#lib/types.js';

const CACHE_KEY = 'word_definitions_cache';
const CACHE_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 days

interface CacheEntry {
    data: DictionaryResponse;
    timestamp: number;
}

interface Cache {
    [word: string]: CacheEntry;
}

/**
 * Retrieves a cached word definition from localStorage
 * @param word - The word to look up
 * @returns The cached definition or null if not found or expired
 */
export function getCachedDefinition(word: string): DictionaryResponse | null {
    try {
        const cache: Cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
        const cached = cache[word.toLowerCase()];

        if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
            return cached.data;
        }

        // Clean up expired entry
        if (cached) {
            delete cache[word.toLowerCase()];
            localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
        }
    } catch (e) {
        console.warn('Cache read error:', e);
    }
    return null;
}

/**
 * Stores a word definition in localStorage cache
 * @param word - The word to cache
 * @param data - The definition data to cache
 */
export function setCachedDefinition(word: string, data: DictionaryResponse): void {
    try {
        const cache: Cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
        cache[word.toLowerCase()] = {
            data,
            timestamp: Date.now()
        };
        localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
    } catch (e) {
        console.warn('Cache write error:', e);
    }
}

/**
 * Clears all cached definitions
 */
export function clearDefinitionCache(): void {
    try {
        localStorage.removeItem(CACHE_KEY);
    } catch (e) {
        console.warn('Cache clear error:', e);
    }
}

/**
 * Gets the size of the cache (number of entries)
 */
export function getCacheSize(): number {
    try {
        const cache: Cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
        return Object.keys(cache).length;
    } catch (e) {
        console.warn('Cache size error:', e);
        return 0;
    }
}
