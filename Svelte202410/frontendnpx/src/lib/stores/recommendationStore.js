import { writable } from 'svelte/store';

export const recommendedMangas = writable([]);
export const userRatings = writable({});  // { mangaId: rating }