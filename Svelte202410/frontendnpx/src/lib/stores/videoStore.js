import { writable } from 'svelte/store';
import { persistStore } from '$lib/persistStore';


export const videoPage = writable(0);
export const keyword = writable("{'etc': ['요약']}");
// // 초기값을 빈 배열로 설정
// export const galleries = writable([]);
// export const imageUrls = writable([]);
// export const currentPage = writable(1);
// export const genres = writable([]); 
// // export const folders = writable([]); // 활성화된 폴더 목록
// export const folderStates = writable({}); // 폴더별 on/off 상태
// export const selectedMangaStore = writable([]); // 선택된 만화 목록
// export const searchStore = writable(''); // 검색어

// // 브라우저 환경에서만 로컬 스토리지를 사용하도록 수정
if (typeof window !== 'undefined') {
    persistStore('videoPage', videoPage);
    persistStore('keyword', keyword);
//     persistStore('galleries', galleries);
//     persistStore('imageUrls', imageUrls);
//     persistStore('currentPage', currentPage);
//     persistStore('genres', genres);
//     persistStore('folderStates', folderStates);
//     persistStore('selectedMangaStore', selectedMangaStore);
    // persistStore('searchStore', searchStore);
}