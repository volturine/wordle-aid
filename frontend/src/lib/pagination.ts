export type PageItem = number | 'gap';

export function paginationItems(current: number, totalPages: number): PageItem[] {
	if (totalPages < 1) return [];
	const wanted = new Set<number>();
	const include = (page: number) => {
		if (page >= 1 && page <= totalPages) wanted.add(page);
	};
	include(1);
	include(totalPages);
	for (let page = current - 2; page <= current + 2; page += 1) include(page);
	if (current <= 4) {
		for (let page = 1; page <= Math.min(5, totalPages); page += 1) include(page);
	}
	if (current >= totalPages - 3) {
		for (let page = Math.max(1, totalPages - 4); page <= totalPages; page += 1) include(page);
	}
	const sorted = [...wanted].sort((left, right) => left - right);
	const items: PageItem[] = [];
	for (const page of sorted) {
		const previous = items.at(-1);
		if (typeof previous === 'number' && page > previous + 1) items.push('gap');
		items.push(page);
	}
	return items;
}
