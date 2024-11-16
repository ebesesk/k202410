<script>
    import fastapi from "$lib/api";
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { writable } from 'svelte/store';
    import { 
        currentPage,        // 현재 페이지  
        folderStates,       // 서버에서 가져올 manga 폴더 목록
        searchStore,        // 검색어
        galleries,          // 서버에서 가져온 manga 목록
        imageUrls,          // 화면에 보여줄 이미지 목록
        genres,             // folderStates 장르 목록
        selectedMangaStore,  // 선택한 망가 이동 & 병합 대상 manga 목록
        sortType,
        orderType,
    } from '$lib/stores/galleryStore';
    import Pagination from '$lib/components/Pagination.svelte';
    import { recommendedMangas, userRatings } from '$lib/stores/recommendationStore';
    import StarRating from '$lib/components/StarRating.svelte';
    import { delSpecialCharacter } from '$lib/util';
    import { access_token, userpoints, is_login } from '$lib/store';
    import { goto } from '$app/navigation';
    import { get } from 'svelte/store'; 

    // onMount 훅
    onMount(() => {
        if (browser) {
            if (!get(is_login)) {
                goto('/');
                return;
            }
            fetchGalleries($currentPage);
        }
    });

    // 페이지 수 및 아이템 수 설정
    let totalPages = 1;
    let pageSize = 20;

    // 통합된 fetch 함수
    async function fetchData(endpoint, options = {}) {
        const baseUrl = 'https://api2410.ebesesk.synology.me';
        let accessToken = '';

        if (browser) {
            accessToken = get(access_token);
        }

        if (!accessToken && !options.skipAuth) {
            console.error('인증 토큰이 없습니다.');
            if (browser) {
                window.location.href = '/';
            }
            return null;
        }

        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Accept': options.isImage ? 'image/*' : 'application/json',
                'Content-Type': 'application/json'
            },
            mode: 'cors'
        };

        try {
            const response = await fetch(`${baseUrl}${endpoint}`, { ...defaultOptions, ...options });

            if (response.status === 401) {
                console.error('인증 토큰이 만료되었습니다.');
                if (browser) {
                    window.location.href = '/';
                }
                return null;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            if (options.isImage) {
                const blob = await response.blob();
                return blob.size > 0 ? URL.createObjectURL(blob) : null;
            }

            return await response.json();
        } catch (error) {
            console.error(`Fetch error for ${endpoint}:`, error);
            throw error;
        }
    }

    // 갤러리 데이터 가져오기
    function fetchGalleries(page, customParams = null) {
        const params = customParams || {
            page: page,
            size: pageSize,
            sort_by: $sortType,
            order: $orderType,
            search: $searchStore,
            folders: Object.entries($folderStates)
                .filter(([_, isActive]) => isActive)
                .map(([genre]) => genre)
        };

        fastapi('get', '/manga/mangas/', params,
            (json) => {
                galleries.set(json.items || []);
                currentPage.set(page);
                totalPages = json.pages;
                pageSize = json.size || 20;
                genres.set(json.genres || []);
                
                if (json.items && json.items.length > 0) {
                    fetchGalleryImages(json.items);
                }
            },
            (err) => {
                console.error('갤러리 데이터를 불러오는데 실패했습니다:', err);
            }
        );
    }

    // 추천 데이터 가져오기
    async function fetchRecommendations() {
        try {
            const data = await fetchData('/manga/recommended/');
            recommendedMangas.set(data.recommendations || []);
            
            if ($recommendedMangas.length > 0) {
                await fetchGalleryImages($recommendedMangas);
            }
        } catch (error) {
            console.error('추천 망가를 불러오는데 실패했습니다:', error);
            recommendedMangas.set([]);
        }
    }

    // 평점 주기
    function rateGallery(mangaId, rating) {
        if ($userRatings[mangaId] === rating) {
            fastapi('delete', `/manga/${mangaId}/rate`, {},
                () => {
                    userRatings.update(ratings => {
                        const newRatings = { ...ratings }
                        delete newRatings[mangaId]
                        return newRatings
                    })
                    // fetchGalleries($currentPage)
                }
            )
        } else {
            fastapi('post', `/manga/${mangaId}/rate`, { rating },
                () => {
                    userRatings.update(ratings => ({
                        ...ratings,
                        [mangaId]: rating
                    }))
                    // fetchGalleries($currentPage)
                }
            )
        }
    }

    // 이미지 URL 가져오기
    function fetchGalleryImages(items) {
        if (!items || items.length === 0) {
            imageUrls.set([]);
            return;
        }

        let urls = Array(items.length).fill(null);
        imageUrls.set(urls);

        items.forEach((item, index) => {
            const imageUrl = getImageUrl(item);
            if (imageUrl) {
                fastapi('get', imageUrl, { isImage: true },
                    (url) => {
                        imageUrls.update(urls => {
                            const newUrls = [...urls];
                            newUrls[index] = url;
                            return newUrls;
                        });
                    },
                    (err) => {
                        console.error(`Error fetching image ${index}:`, err);
                    }
                );
            }
        });
    }

    // 사용자 평점 데이터 가져오기
    async function fetchUserRatings() {
        try {
            const data = await fetchData('/manga/user-ratings/');
            const ratings = {};
            data.forEach(rating => {
                ratings[rating.manga_id] = rating.rating;
            });
            userRatings.set(ratings);
        } catch (error) {
            console.error('사용자 평점을 불러오는데 실패했습니다:', error);
            userRatings.set({});
        }
    }

    // onMount 수정
    onMount(async () => {
        try {
            await Promise.all([
                fetchGalleries($currentPage),
                fetchRecommendations(),
                fetchUserRatings()  // 사용자 평점 데이터 가져오기 추가
            ]);
        } catch (error) {
            console.error('초기 데이터 로딩 실패:', error);
        }
    });

    // 이미지 URL 생성
    const getImageUrl = (item, imageNum = false) => {
        try {
            const folder_name = item.folder_name
                .replace('/home/manga/', '')
                .split('/')
                .map(part => encodeURIComponent(part))
                .join('/');
            
            const images = JSON.parse(item.images_name);
            const image_ext = ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'];
            
            let targetImages = imageNum !== false 
                ? [...images.slice(imageNum), ...images.slice(0, imageNum)]
                : images;

            const validImage = targetImages.find(img => {
                const ext = img.split('.').pop().toLowerCase();
                const fileName = img.split('/').pop();
                return image_ext.includes(ext) && fileName;
            });

            if (!validImage) {
                console.error('No valid image found in:', images);
                return null;
            }

            const fileName = validImage.split('/').pop();
            return `/images/${folder_name}/${encodeURIComponent(fileName)}`;
        } catch (error) {
            console.error('Error in getImageUrl:', error);
            return null;
        }
    }

    
    // 페이지 변경 핸들러
    async function handlePageChange(newPage) {
        try {
            if (newPage >= 1 && newPage <= totalPages) {
                const activeGenres = Object.entries($folderStates)
                    .filter(([_, isActive]) => isActive)
                    .map(([genre]) => genre);

                const params = {
                    page: newPage,
                    size: pageSize,
                    sort_by: $sortType,
                    order: $orderType,
                    search: $searchStore
                };

                if (activeGenres.length > 0) {
                    params.folders = activeGenres;  // 배열로 전달
                }

                fetchGalleries(newPage, params);
            }
        } catch (error) {
            console.error('페이지 변경 중 오류:', error);
        }
    }

    let currentImageIndexes = Array($galleries.length).fill(0);	// 이미지 순서 변수
    let imagesNum = Array($galleries.length).fill(0);	// 이미지 순서 변수
	
    async function handleImageClick(galleryIndex, direction) {
        const gallery = $galleries[galleryIndex];
        const images = JSON.parse(gallery.images_name);
        
        if (!currentImageIndexes[galleryIndex]) {
            currentImageIndexes[galleryIndex] = 0;
        }

        if (direction === 'next') {
            currentImageIndexes[galleryIndex] = (currentImageIndexes[galleryIndex] + 1) % images.length;
        } else if (direction === 'prev') {
            currentImageIndexes[galleryIndex] = (currentImageIndexes[galleryIndex] - 1 + images.length) % images.length;
        }

        const imageUrl = getImageUrl(gallery, currentImageIndexes[galleryIndex]);
        if (imageUrl) {
            const newImageUrl = await fetchData(imageUrl, { isImage: true });
            imageUrls.update(urls => {
                const newUrls = [...urls];
                newUrls[galleryIndex] = newImageUrl;
                return newUrls;
            });
        }
    }

    function exist_zip(images_name) {
        const zip_ext = ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'alz'];
        images_name = JSON.parse(images_name);
        for (let j = 0; j < images_name.length; j++) {
            for (let k = 0; k < zip_ext.length; k++) {
                if (images_name[j].endsWith(zip_ext[k])) {
                    return images_name[j];
                }
            }
        }
        return false;
    }

    // 장르 상태 관리
    let selectedGenres = {};
    
    // 장르 버튼 토글
    function toggleGenre(genre) {
        folderStates.update(states => ({
            ...states,
            [genre]: !states[genre] // 선택된 장르의 상태값만 반전시킵니다
        }));
    }

    // 필터 적용
    async function applyFilter() {
        try {
            currentPage.set(1);
            
            const activeGenres = Object.entries($folderStates)
                .filter(([_, isActive]) => isActive)
                .map(([genre]) => genre);
                
            const params = new URLSearchParams({
                page: 1,
                size: pageSize,
                sort_by: 'id',
                order: 'desc'
            });

            if (activeGenres.length > 0) {
                activeGenres.forEach(genre => {
                    params.append('folders', genre);
                });
            }

            const data = await fetchData(`/manga/mangas/?${params.toString()}`);
            if (data) {
                galleries.set(data.items || []);
                if (data.total_items) {
                    totalPages = Math.ceil(data.total_items / pageSize);
                } else {
                    totalPages = data.pages || Math.ceil(data.items.length / pageSize);
                }
                pageSize = data.size || 20;
                fetchGalleryImages($galleries);
            }
        } catch (error) {
            console.error('갤러리 데이터를 불러오는데 실패했습니다:', error);
        }
    }

    // 검색 함수 수정
    async function handleSearch(searchTerm) {
        try {
            const activeGenres = Object.entries($folderStates)
                .filter(([_, isActive]) => isActive)
                .map(([genre]) => genre);

            const params = new URLSearchParams({
                page: 1,
                size: pageSize,
                sort_by: 'id',
                order: 'desc'
            });

            if (searchTerm) {
                params.append('search', searchTerm);
            }

            if (activeGenres.length > 0) {
                activeGenres.forEach(genre => {
                    params.append('folders', genre);
                });
            }

            const data = await fetchData(`/manga/mangas/?${params.toString()}`);
            if (data) {
                galleries.set(data.items || []);
                currentPage.set(1);
                totalPages = data.pages || 1;
                pageSize = data.size || 20;
                await fetchGalleryImages($galleries);
            }
        } catch (error) {
            console.error('검색 중 오류 발생:', error);
        }
    }

    // 디바운스 처리
    function debounceSearch() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            handleSearch();
        }, 300);  // 300ms 대기
    }

    let selectedIndex = 0;
    let showModal = false;

    function openModal(i) {
        selectedIndex = i;
        showModal = true;
    }

    function closeModal() {
        showModal = false;
    }

    // let sortType = 'id';
    // let orderType = 'desc';

    async function handleSort(newSortType, newOrderType) {
        try {
            $sortType = newSortType; // 현재 정렬 타입 업데이트
            $orderType = newOrderType;
            const params = new URLSearchParams({
                page: $currentPage,
                size: pageSize,
                sort_by: newSortType,
                order: $orderType
            });

            if ($searchStore) {
                params.append('search', $searchStore);
            }

            const activeGenres = Object.entries($folderStates)
                .filter(([_, isActive]) => isActive)
                .map(([genre]) => genre);

            if (activeGenres.length > 0) {
                activeGenres.forEach(genre => {
                    params.append('folders', genre);
                });
            }

            const data = await fetchData(`/manga/mangas/?${params.toString()}`);
            if (data) {
                galleries.set(data.items || []);
                await fetchGalleryImages($galleries);
            }
        } catch (error) {
            console.error('정렬 중 오류 발생:', error);
        }
    }

    const folderVisibility = writable({});
    function getDisplayFolderName(folderName) {
        return folderName.split('/').pop();
    }

    // 버튼 상태를 저장할 배열 (true: on, false: off)
    let buttonStates = Array(10).fill(false);
    function handleHeaderButton(buttonNum) {
        buttonStates[buttonNum - 1] = !buttonStates[buttonNum - 1];
    }

    // 파일 이동 병합 관련
    let selectedAction = null; // 이동 & 병합    
    let targetGenre = '';
    let targetTitle = ''; // 대상 서브 폴더 이름
    $: targetFolderName = targetTitle ? `${targetGenre}/${targetTitle}` : targetGenre; // 대상 폴더 이름

    // 파일 이름 업데이트 함수
    function updateTargetFolderName(selectedIds) {
        if (selectedIds.length > 0) {
            const firstGallery = $galleries.find(g => g.id === selectedIds[0]);
            if (firstGallery) {
                targetGenre = firstGallery.folder_name.split('/')[0];
                targetTitle = firstGallery.folder_name.split('/')[1];
            }
        } else {
            targetTitle = '';
        }
    }

    // galleries 에서 폴더이름 추출
    function getFolderName() {
        let manga = $galleries.find(gallery => gallery.id === $selectedMangaStore[0]);
        if (manga) {
            return manga.folder_name;
        }
    }

    // 라디오 버튼 핸들러 함수 수정
    function selectManga(mangaId) {
        selectedMangaStore.update(items => {
            const index = items.indexOf(mangaId);
            const newItems = index === -1 
                ? [...items, mangaId]  // 추가
                : items.filter(id => id !== mangaId);  // 제거
            updateTargetFolderName(newItems);
            return newItems;
        });
    }

    // 원본 이름 추출 함수 추가
    function getOriginalName(folderName) {
        if (!folderName) return '';
        const parts = folderName.split('/');
        return parts[parts.length - 1] || '';
    }

    // manga 합치거나 폴더 이동 함수, 액션 처리 함수 파일 관리
    let mangasActionResult = [];

    async function handleAction() {
        if (!selectedAction || !targetFolderName || $selectedMangaStore.length === 0) return;

        try {
            const endpoint = '/manga/manga-actions/';
            const result = await fetchData(endpoint, {
                method: 'POST',
                body: JSON.stringify({
                    action: selectedAction,
                    target_folder_name: targetFolderName,
                    manga_ids: $selectedMangaStore,
                })
            });
            mangasActionResult = result;
            selectedMangaStore.set([]);
            selectedAction = null; // 이동 & 병합
            targetGenre = ''; // 대상 장르 폴더 이름
            targetTitle = ''; // 대상 서브 폴더 이름
            
            // 갤러리 목록 새로고침
            await fetchGalleries($currentPage);

        } catch (error) {
            console.error(`${selectedAction} 처리 중 오류 발생:`, error);
        }
    }

    async function dbUpdate(genre_name) {
        const endpoint = '/manga/bulk-update';
        const params = new URLSearchParams({
            genre_name: genre_name
        });
        const result = await fetchData(`${endpoint}?${params.toString()}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    
    // 검색어가 변경될 때마다 갤러리 데이터 다시 불러오기
    $: if ($searchStore !== undefined) {
        handleSearch($searchStore);
    }

    // selectedMangaStore 구독하여 첫 선택 시 이름 설정
    $: if ($selectedMangaStore.length > 0) {
        const selectedManga = $galleries.find(g => g.id === $selectedMangaStore[0]);
        if (selectedManga) {
            const folderName = selectedManga.folder_name;
            if (selectedAction === 'move') {
                targetGenre = folderName.split('/')[0];
                targetTitle = '';
            } else {
                targetGenre = folderName.split('/')[0];
                targetTitle = folderName.split('/')[1];
            }
        }   
    }

    // 초기 상태 설정
    $: if ($genres.length > 0 && Object.keys($folderStates).length === 0) {
        const initialStates = {};
        $genres.forEach(genre => {
            initialStates[genre] = false;
        });
        folderStates.set(initialStates);
    }


    // video.dbid를 클릭할 때 조회수 증가
    const incrementViewCount = (mangaId) => {
        fastapi('post', 
            `/manga/${mangaId}/view`, 
            {},
            (json) => {
                // 성공 시 처리 (필요한 경우)
                console.log('조회수 증가 성공:', json);
            },
            (err) => {
                // 실패 시 처리
                console.error('조회수 증가 실패:', err);
            }
        );
    };
</script>
{#if $is_login}
<!-- gallery-header 부분 수정 -->
<div class="gallery-header">
    <div class="button-container">
        <!-- 첫 번째 줄: 정렬 버튼들 -->
        <div class="button-row sort-buttons">
            <div class="spacer"></div>
            <button class="header-button {$sortType === 'page' ? 'active' : ''}" on:click={() => handleSort('page', 'desc')}>
                page
            </button>
            <button class="header-button {$sortType === 'file_date' ? 'active' : ''}" on:click={() => handleSort('file_date', 'desc')}>
                파일 날짜순
            </button>
            <button class="header-button {$sortType === 'update_date' ? 'active' : ''}" on:click={() => handleSort('update_date', 'desc')}>
                최신순
            </button>
            <button class="header-button {$sortType === 'rating' ? 'active' : ''}" on:click={() => handleSort('rating', 'desc')}>
                평점순
            </button>
            <button class="header-button {$sortType === 'id' ? 'active' : ''}" on:click={() => handleSort('id', 'desc')}>
                기본순
            </button>
            <button class="header-button {$orderType === 'asc' ? 'active' : ''}" on:click={() => handleSort($sortType, 'asc')}>
                오름차순
            </button>
            <button class="header-button {$orderType === 'random' ? 'active' : ''}" on:click={() => handleSort($sortType, 'random')}>
                랜덤
            </button>
        </div>

        <!-- 두 번째 줄: 장르 버튼들과 적용 버튼 -->
        <div class="button-row genre-buttons">
            <div class="spacer"></div>
            {#each $genres as genre}
                <button class="header-button {$folderStates[genre] ? 'active' : ''}" on:click={() => toggleGenre(genre)}>
                    {genre.replace('__', '')}
                    <span class="status-indicator">
                        {$folderStates[genre] ? 'ON' : 'OFF'}
                    </span>
                </button>
            {/each}
            <button class="header-button submit-button" on:click={applyFilter}>
                적용
            </button>
        </div>

        <!-- 선택된 항목이 있을 때 표시할 작업 선택 영역 -->
        <div class="button-row genre-buttons">
            <div class="selected-items">
                {#if $selectedMangaStore.length > 0 || mangasActionResult.length > 0}
                    <div class="selection-info">
                        <div class="button-row action-panel">
                            {#if $selectedMangaStore.length > 0}
                            <div class="action-container">
                                <div class="name-input-area">
                                    <div class="input-wrapper">
                                        <input 
                                            type="text"
                                            class="folder-name-input"
                                            bind:value={targetFolderName}
                                            placeholder="대상 폴더 이름"
                                        />
                                    </div>
                                    <small>
                                        <button 
                                            class="reset-name-button"
                                            on:click={() => {
                                                const selectedManga = $galleries.find(g => g.id === $selectedMangaStore[0]);
                                                const folderName = selectedManga.folder_name;
                                                if (selectedManga && selectedAction === 'move') {
                                                    targetGenre = folderName.split('/')[0];
                                                    targetTitle = '';
                                                } else {
                                                    targetGenre = folderName.split('/')[0];
                                                    targetTitle = folderName.split('/')[1];
                                                }
                                            }}
                                        >
                                            원래 이름으로
                                        </button>
                                    </small>
                                </div>

                                <div class="folder-selection">
                                    {#if targetGenre && $selectedMangaStore.length > 1}
                                        <div class="merge-preview">
                                            <small>
                                                {#if selectedAction === 'move'}
                                                    병합 후 경로: {targetGenre}
                                                {:else}
                                                    이동 후 경로: {targetGenre}/{targetTitle}
                                                {/if}
                                            </small>
                                        </div>
                                    {/if}
                                    <div class="radio-group">
                                        <label class="radio-label">
                                            <input 
                                                type="radio" 
                                                name="action" 
                                                value="move"
                                                bind:group={selectedAction}
                                                on:click={() => {
                                                    selectedAction = 'move';
                                                }}
                                            >
                                            <span class="radio-text">이동</span>
                                        </label>
                                        <label class="radio-label">
                                            <input 
                                                type="radio" 
                                                name="action" 
                                                value="merge"
                                                bind:group={selectedAction}
                                                on:click={() => {
                                                    selectedAction = 'merge';
                                                }}  
                                            >
                                            <span class="radio-text">병합</span>
                                        </label>
                                    </div>
                                    
                                    <select class="folder-select" bind:value={targetGenre}>
                                        <option value="">폴더 선택</option>
                                        {#each $genres as genre}
                                            <option value={genre}>{genre}</option>
                                        {/each}
                                    </select>
                                    <div class="action-buttons">
                                        <button 
                                            class="action-button"
                                            disabled={!selectedAction || !targetFolderName}
                                            on:click={handleAction}
                                        >
                                            실행
                                        </button>
                                        <button 
                                            class="cancel-button"
                                            on:click={() => {
                                                selectedMangaStore.set([]);
                                                selectedAction = '';
                                                targetGenre = '';
                                                targetTitle = '';
                                            }}
                                        >
                                            취소
                                        </button>
                                        <button 
                                            class="action-button"
                                            disabled={!targetGenre}
                                            on:click={() => dbUpdate(targetGenre)}
                                        >
                                            dbUpdate
                                        </button>
                                    </div>
                                </div>
                            </div>
                            {/if}

                        </div>
                        {#each $selectedMangaStore as mangaId, i}
                        <div class="selected-files3">
                            <button 
                                class="selected-source-file-name"
                                type="button"
                                on:click={() => {
                                    let folderName = $galleries.find(gallery => gallery.id === mangaId)?.folder_name;
                                    if (selectedAction === 'move') {
                                        targetGenre = folderName.split('/')[0];
                                        targetTitle = '';
                                    } else {
                                        targetGenre = folderName.split('/')[0];
                                        targetTitle = folderName.split('/')[1];
                                    }
                                }}
                            >
                                {mangaId}. {$galleries.find(gallery => gallery.id === mangaId)?.folder_name}
                            </button>
                            <button 
                                class="remove-selection"
                                on:click={() => {
                                    selectedMangaStore.update(items => {
                                        const newItems = items.filter(id => id !== mangaId);
                                        updateTargetFolderName(newItems);
                                        return newItems;
                                    });
                                }}
                            >
                                ×
                            </button>
                        </div>
                        {/each}
                        {#if mangasActionResult.length > 0}
                        <div class="selected-files3 manga-action-result">
                            {#each mangasActionResult as manga}
                                <div class="manga-action-result-item">
                                    {manga.manga.id} {manga.manga.folder_name} {manga.msg}
                                </div>
                                <button 
                                    class="remove-selection"
                                    on:click={() => {
                                        mangasActionResult = []
                                    }}
                                >
                                    ×
                                </button>
                            {/each}
                        </div>
                        {/if}
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div>

<div class="pagination-container">
    <Pagination
        totalPages={totalPages}
        currentPage={$currentPage}
        on:pageChange={(e) => handlePageChange(e.detail)}
    />
</div>

{#if showModal}
<div class="modal-backdrop">
    <div 
        class="modal-content" 
        on:click|stopPropagation
        on:keydown|stopPropagation
        role="presentation">
        {#if $imageUrls[selectedIndex] && typeof $imageUrls[selectedIndex] === 'string'}
        <div class="modal-image-wrapper">
            <div class="folder-name-wrapper">
                <div class="folder-name" style="position: absolute; z-index: 1; top: 0;">{$galleries[selectedIndex].folder_name}</div>
            </div>
            <img src={$imageUrls[selectedIndex]} alt={$galleries[selectedIndex].folder_name} class="modal-image" />
            <button type="button" class="close-button" on:click={closeModal}>닫기×</button>
            <button
                type="button"
                class="modal-nav-button prev"
                on:click|stopPropagation={() => handleImageClick(selectedIndex, 'prev')}
            >◀</button>
            <button 
                type="button"
                class="modal-nav-button next"
                on:click|stopPropagation={() => handleImageClick(selectedIndex, 'next')}
            >▶</button>
        </div>
        {/if}
    </div>
</div>
{/if}

<!-- 기존 갤러리 목록에도 평점 기능 추가 -->
<div class="gallery-container">
    <div class="galleries">
        {#each $galleries as gallery, i}
        <div class="gallery-item {$selectedMangaStore.includes(gallery.id) ? 'selected' : ''}">
            <button class="image-button" on:click={() => openModal(i)}>
                <small>{gallery.id}. {gallery.folder_name.split('/')[0]}<br></small>    
                <small>{gallery.folder_name.split('/')[1].slice(0, 21)}</small>
            </button>
            {#if $imageUrls[i] && typeof $imageUrls[i] === 'string'}
                <div class="image-container">
                    <img src={$imageUrls[i]} alt={gallery.folder_name} />
                    <button 
                        type="button"
                        class="nav-button prev"
                        on:click|stopPropagation={() => handleImageClick(i, 'prev')}
                        on:keydown|stopPropagation={e => e.key === 'Enter' && handleImageClick(i, 'prev')}
                    >◀</button>
                    <button 
                        type="button"
                        class="nav-button next"
                        on:click|stopPropagation={() => handleImageClick(i, 'next')}
                        on:keydown|stopPropagation={e => e.key === 'Enter' && handleImageClick(i, 'next')}
                    >▶</button>
                </div>
            {:else}
                <p>이미지 로딩 중...</p>
            {/if}
            <div class="rating-container">
                <div class="rating-row">
                    <StarRating 
                        value={$userRatings[gallery.id] || 0}
                        onChange={(rating) => rateGallery(gallery.id, rating)}
                    />
                    {#if $userRatings[gallery.id]}
                        <button 
                            type="button" 
                            class="delete-rating" 
                            on:click={() => rateGallery(gallery.id, $userRatings[gallery.id])}
                            title="평점 삭제">
                            ×
                        </button>
                    {/if}
                </div>
                {#if exist_zip(gallery.images_name) === false}
                    <a 
                        href="{'kddddds2://http://' + gallery.folder_name}" 
                        style="font-size: 0.9em;"
                        on:click={() => incrementViewCount(gallery.id)}>
                        <span class="average-rating">
                            평균: {gallery.rating_average ? gallery.rating_average.toFixed(1) : '0.0'}
                            ⇒{JSON.parse(gallery.images_name).length}p
                        </span>
                    </a>
                {:else}
                    <a 
                        href="{'kddddds2://http://'+ exist_zip(gallery.images_name)}"
                        style="font-size: 0.9em;"
                        on:click={() => incrementViewCount(gallery.id)}>
                        <span class="average-rating">
                            평균: {gallery.rating_average ? gallery.rating_average.toFixed(1) : '0.0'}
                            ⇒{JSON.parse(gallery.tags)['size']}        
                        </span>
                    </a>
                {/if}
                {#if $userpoints >= 1000}
                <small>
                    <label class="radio-label">
                        <input
                            type="checkbox"
                            name="gallery-{gallery.id}"
                            value="option1"
                            checked={$selectedMangaStore.includes(gallery.id)}
                            on:change={() => selectManga(gallery.id)}
                        />
                        <span class="radio-text">선택</span>
                    </label>
                </small>
                {/if}
            </div>
        </div>
        {/each}
    </div>
</div>

<div class="pagination-container">
    <Pagination
        totalPages={totalPages}
        currentPage={$currentPage}
        on:pageChange={(e) => handlePageChange(e.detail)}
    />
</div>
{/if}
<style>
    .gallery-container {
        width: 100%;
        padding: 10px;
        box-sizing: border-box;
        margin-bottom: 60px;  /* 페이지네이션 높이만큼 마진 */
    }

    .galleries {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;  /* 간격 살짝 줄임 */
        width: 100%;
        max-width: 1200px;  /* 전체 컨테이너 너비 줄임 (1400px → 1200px) */
        margin: 0 auto;
    }

    .gallery-item {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        transition: all 0.2s ease;  /* transition 속성 추가 */
        max-width: 200px;
        margin: 0 auto;
        background: white;  /* 기본 배경색 추가 */
    }

    .gallery-item img {
        width: 100%;
        aspect-ratio: 3/4;
        object-fit: cover;
        border-radius: 4px;
    }
    
    /* 선택된 아이템 스타일 */
    .gallery-item.selected {
        border-color: #2196F3;  /* 파란색 테두리 */
        background-color: #E3F2FD;  /* 연한 파란색 배경 */
        box-shadow: 0 0 8px rgba(33, 150, 243, 0.2);  /* 그림자 효과 */
    }

    /* 선택적: 선택된 아이템의 이미지 테두리도 강조 */
    .gallery-item.selected img {
        border: 2px solid #2196F3;
    }

    /* 선택적: 선택된 아이템의 텍스트 색상도 변경 */
    .gallery-item.selected .image-button small {
        color: #1976D2;
        font-weight: 500;
    }

    /* 선택된 상태의 hover 효과 */
    .gallery-item.selected:hover {
        transform: scale(1.02);
        background-color: #BBDEFB;  /* 더 진한 파란색 배경으로 변경 */
    }

    .gallery-item:hover {
        transform: scale(1.02);
        border-color: #2196F3;
    }

    .gallery-header {
        overflow: hidden;
        font-size: 0.8rem;
        padding: 0.2rem;
        display: inline;
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 100;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 반응형 그리드 */
    @media (max-width: 1200px) {
        .galleries {
            grid-template-columns: repeat(4, 1fr);  /* 4열 */
        }
    }

    @media (max-width: 992px) {
        .galleries {
            grid-template-columns: repeat(3, 1fr);  /* 3열 */
        }
    }

    @media (max-width: 768px) {
        .galleries {
            grid-template-columns: repeat(2, 1fr);  /* 2열 */
            gap: 10px;
        }
        
        .gallery-item {
            padding: 8px;
        }
    }

    @media (max-width: 480px) {
        .galleries {
            grid-template-columns: repeat(1, 1fr);  /* 1열 */
        }
        
        .gallery-container {
            padding: 5px;
        }
    }
    
    .image-button {
        width: 100%;
        padding: 0;
        border: none;
        background: none;
        cursor: pointer;
    }

    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .close-button {
        position: absolute;
        top: 30px;
        right: 30px;
        padding: 30px;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        cursor: pointer;
        z-index: 1001;
        border-radius: 4px;
    }

    .rating-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        margin-top: 0.5rem;
    }

    .rating-row {
        display: flex;
        align-items: center;
        gap: 0.25rem;  /* 별점과 삭제 버튼 사이 간격 */
    }

    .delete-rating {
        background: none;
        border: none;
        color: #ff4444;
        cursor: pointer;
        font-size: 0.9em;
        padding: 2px 4px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 16px;
        height: 16px;
        min-width: 16px;  /* 크기 고정 */
        line-height: 1;
    }

    .delete-rating:hover {
        background: rgba(255, 68, 68, 0.1);
    }

    .average-rating {
        font-size: 0.8em;
        color: #666;
    }

    .image-container {
        position: relative;
        width: 100%;
    }

    .nav-button {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(0, 0, 0, 0.3);
        color: white;
        border: none;
        padding: 5px 10px;
        cursor: pointer;
        z-index: 2;
        opacity: 0;  /* 기본적으로 숨김 */
        transition: opacity 0.3s ease;  /* 부드러운 전환 효과 */
    }

    .image-container:hover .nav-button {
        opacity: 1;  /* 호버링 시 보이게 함 */
    }

    .nav-button:hover {
        background: rgba(0, 0, 0, 0.5);  /* 버튼 호버링 시 더 진한 배경 */
    }

    .prev {
        left: 0;
    }

    .next {
        right: 0;
    }

    .modal-content img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }

    .modal-content {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
    }

    .modal-nav-button {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        padding: 20px 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .modal-content:hover .modal-nav-button {
        opacity: 1;
    }

    .close-button {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        z-index: 2;
    }

    .close-button:hover {
        background: rgba(0, 0, 0, 0.7);
    }

    .modal-image-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;  /* 추가: 뷰포트 높이만큼 설정 */
    }

    .modal-image {
        max-width: 50%;
        height: 80vh;  /* 수정: 뷰포트 높이로 설정 */
        object-fit: contain;  /* 이미지 비율 유지 */
        display: flex;
        margin: auto;
        align-items: center;
        justify-content: center;
    }

    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @media (max-width: 768px) {
        .gallery-header {
            flex-direction: column;
            gap: 1rem;
        }
    }

    /* 모바일 반응형 */
    @media (max-width: 768px) {
        .button-container {
            flex-wrap: wrap;
        }
    }

    .button-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
        background-color: white;
    }

    .button-row {
        display: flex;
        gap: 4px;
        flex-wrap: wrap;
        width: 100%;
    }

    .spacer {
        flex-grow: 1;  /* 왼쪽 공간을 최대한 차지 */
    }

    .sort-buttons {
        justify-content: flex-end;  /* 오른쪽 정렬 */
        padding-bottom: 4px;
        border-bottom: 1px solid #eee;
    }

    .genre-buttons {
        justify-content: flex-end;  /* 오른쪽 정렬 */
        overflow-x: auto;
        padding-bottom: 4px;
    }

    .header-button {
        padding: 4px 8px;
        background: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 3px;
        cursor: pointer;
        white-space: nowrap;
        transition: all 0.2s;
        display: flex;
        gap: 4px;
        align-items: center;
        font-size: 0.8rem;
        flex-shrink: 0;  /* 버튼 크기 유지 */
    }

    .header-button.active {
        background: #4CAF50;
        color: white;
        border-color: #45a049;
    }

    .submit-button {
        background-color: #2196F3;
        color: white;
    }

    .submit-button:hover {
        background-color: #1976D2;
    }

    .status-indicator {
        font-size: 0.7em;
        padding: 1px 4px;
        border-radius: 2px;
        background: rgba(0, 0, 0, 0.1);
    }

    .active .status-indicator {
        background: rgba(255, 255, 255, 0.2);
    }

    @media (max-width: 768px) {
        .button-row {
            justify-content: flex-end;
        }
        .gallery-item.selected {
            box-shadow: 0 0 6px rgba(33, 150, 243, 0.3);
        }
        .sort-buttons {
            border-bottom: none;
        }
        
        .spacer {
            display: none;  /* 모바일에서는 spacer 숨김 */
        }
    }

    .pagination-container {
        display: flex;
        justify-content: center;  /* 가운데 정렬 */
        align-items: center;
        width: 100%;
        padding: 1rem 0;
        margin: 1rem 0;
    }

    .selection-info {
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .radio-text {
        font-size: 0.875rem;
        color: #333;
    }

    .remove-selection {
        background: none;
        border: none;
        color: #ff4444;
        cursor: pointer;
        padding: 0 0.25rem;
        font-size: 1rem;
        line-height: 1;
    }

    .name-input-area {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        width: 100%;
    }

    .input-wrapper {
        flex: 1;
        position: relative;
        min-width: 0;  /* 컨테이너가 줄어들 수 있도록 설정 */
        display: flex;
    }

    .remove-selection:hover {
        color: #ff0000;
    }

    @media (max-width: 768px) {
        .action-button {
            width: 100%;
        }
    }

    @media (max-width: 768px) {
        .name-input-area {
            flex-direction: column;
        }

        .reset-name-button {
            width: 100%;
        }
    }

    .folder-name-input {
        width: 800px;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.875rem;
        min-width: 0;  /* 입력창이 줄어들 수 있도록 설정 */
        overflow-x: auto;  /* 가로 스크롤 허용 */
        white-space: nowrap;  /* 텍스트 줄바꿈 방지 */
    }

    /* 스크롤바 스타일링 (선택사항) */
    .folder-name-input::-webkit-scrollbar {
        height: 4px;
    }

    .folder-name-input::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    .folder-name-input::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 2px;
    }

    .folder-name-input::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    .folder-name-input:focus {
        outline: none;
        border-color: #2196F3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
    }

    .action-panel {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }

    .action-container {
        display: inline;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .folder-selection {
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
    }

    .folder-select {
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        min-width: 200px;
    }

    .name-input-area {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.3rem;
        width: 100%;
    }

    .reset-name-button {
        padding: 0.25rem 0.75rem;
        background: #e0e0e0;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.875rem;
        color: #333;
        white-space: nowrap;
        flex-shrink: 0;  /* 버튼 크기 고정 */
    }

    .reset-name-button:hover {
        background: #d0d0d0;
    }

    @media (max-width: 768px) {
        .name-input-area {
            flex-direction: column;
        }

        .folder-name-input {
            width: 100%;
        }

        .reset-name-button {
            width: 100%;
        }
    }

    .action-button {
        display: inline;
        padding: 0.25rem 0.75rem;
        background: #2196F3;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.875rem;
    }

    .action-button:disabled {
        background: #ccc;
        cursor: not-allowed;
    }

    .cancel-button {
        display: inline;
        padding: 0.25rem 0.75rem;
        background: #f44336;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.875rem;
    }

    .radio-group {
        display: flex;
        gap: 1rem;
    }

    .radio-label {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    .radio-text {
        font-size: 0.9rem;
    }

    @media (max-width: 768px) {
        .folder-selection {
            flex-direction: column;
            align-items: stretch;
        }

        .action-buttons {
            justify-content: stretch;
        }

        .action-button, .cancel-button {
            flex: 1;
        }
    }

    .merge-preview {
        font-size: 0.9rem;
        color: #2196F3;
        margin-top: 0.5rem;
        word-break: break-all;
        max-width: 100%;
        overflow-wrap: break-word;
    }

    .selected-source-file-name {
        display: inline-block;
        max-width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background: none;
        border: none;
        padding: 0;
        text-align: left;
        cursor: pointer;
    }
</style>