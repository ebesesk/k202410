
import { persistStore } from '$lib/persistStore';

// 갤러리 목록을 저장하는 store (배열)
export const galleries = persistStore('galleries', []);

// 각 갤러리의 이미지 URL을 저장하는 store (배열)
export const imageUrls = persistStore('imageUrls', []);

// 현재 페이지 번호를 저장하는 store
export const currentPage = persistStore('currentPage', 1);

