import { writable } from 'svelte/store';
import { persistStore } from '$lib/persistStore';

// 초기값을 빈 배열로 설정
export const galleries = writable([]);
export const imageUrls = writable([]);
export const currentPage = writable(1);

// 브라우저 환경에서만 로컬 스토리지를 사용하도록 수정
if (typeof window !== 'undefined') {
    persistStore('galleries', galleries);
    persistStore('imageUrls', imageUrls);
    persistStore('currentPage', currentPage);
}