<script>
	
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { writable } from 'svelte/store';  // writable import 추가
	import { 
		galleries, 
		imageUrls, 
		currentPage, 
		genres,
		folderStates
	} from '$lib/stores/galleryStore';
	import { searchStore } from '$lib/stores/searchStore';
	import Pagination from '$lib/components/Pagination.svelte';
	import { recommendedMangas, userRatings } from '$lib/stores/recommendationStore';
  import StarRating  from '$lib/components/StarRating.svelte';  // 새로 만들 컴포넌트

    

	// 전체 페이지 수 (서버에서 받은 총 아이템 수를 pageSize로 나눈 값)
	let totalPages = 1;
	// 한 페이지당 보여줄 갤러리 아이템 수 (API 요청 시 사용)
	let pageSize = 20;

		
// 통합된 fetch 함수
async function fetchData(endpoint, options = {}) {
        const baseUrl = 'https://api2410.ebesesk.synology.me';
        let accessToken = '';
        
        if (browser) {  // browser 체크 추가
            accessToken = localStorage.getItem('accessToken');
        }
        
        if (!accessToken && !options.skipAuth) {
            console.error('인증 토큰이 없습니다.');
            if (browser) {  // browser 체크 추가
                window.location.href = '/login';
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
            const response = await fetch(
                `${baseUrl}${endpoint}`, 
                { ...defaultOptions, ...options }
            );

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

// fetchGalleries 함수 수정
async function fetchGalleries(page) {
    try {
        const activeGenres = Object.entries($folderStates)
            .filter(([_, isActive]) => isActive)
            .map(([genre]) => genre);

        const params = new URLSearchParams({
            page: page,
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
        console.log('API 전체 응답:', data); // 전체 응답 데이터 확인

        if (data) {
            galleries.set(data.items || []);
            currentPage.set(page);
            // 전체 페이지 수 계산 (total_items가 있다고 가정)
            if (data.total_items) {
                totalPages = Math.ceil(data.total_items / pageSize);
            } else {
                totalPages = data.pages || Math.ceil(data.items.length / pageSize);
            }
            pageSize = data.size || 20;
            genres.set(data.genres || []);
            
            console.log('페이지 정보 업데이트:', {
                currentPage: page,
                totalPages,
                totalItems: data.total_items,
                pageSize,
                itemsCount: data.items.length
            });

            await fetchGalleryImages($galleries);
        }
    } catch (error) {
        console.error('갤러리 데이터를 불러오는데 실패했습니다:', error);
    }
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
async function rateGallery(mangaId, rating) {
    try {
        if ($userRatings[mangaId] === rating) {
            await fetchData(`/manga/${mangaId}/rate`, {
                method: 'DELETE'
            });
            
            userRatings.update(ratings => {
                const newRatings = { ...ratings };
                delete newRatings[mangaId];
                return newRatings;
            });
        } else {
            await fetchData(`/manga/${mangaId}/rate`, {
                method: 'POST',
                body: JSON.stringify({ rating })
            });

            userRatings.update(ratings => ({
                ...ratings,
                [mangaId]: rating
            }));
        }

        // 현재 검색어와 페이지 상태를 유지하면서 갤러리 데이터 새로고침
        const params = new URLSearchParams({
            page: $currentPage,
            size: pageSize,
            sort_by: 'id',
            order: 'desc'
        });

        // 현재 검색어가 있다면 추가
        if ($searchStore) {
            params.append('search', $searchStore);
        }

        // 활성화된 장르/폴더 추가
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

        await fetchRecommendations();
    } catch (error) {
        console.error('평점 처리에 실패했습니다:', error);
    }
}

// 이미지 가져오기
async function fetchGalleryImages(items) {
    if (!items || items.length === 0) {
        imageUrls.set([]);
        return;
    }

    let urls = Array(items.length).fill(null);
    imageUrls.set(urls);

    for (let i = 0; i < items.length; i++) {
        try {
            const imageUrl = getImageUrl(items[i]);
            if (imageUrl) {
                urls[i] = await fetchData(imageUrl, { isImage: true });
                imageUrls.set(urls);
            }
        } catch (error) {
            console.error(`Error fetching image ${i}:`, error);
        }
    }
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
function getImageUrl(item, imageNum = false) {
    try {
        // 폴더 경로에서 /home/manga/ 부분 제거
        const folder_name = item.folder_name
            .replace('/home/manga/', '')  // 기본 경로 제거
            .split('/')
            .map(part => encodeURIComponent(part))
            .join('/');
        
        const images = JSON.parse(item.images_name);
        const image_ext = ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'];
        
        let targetImages = imageNum !== false 
            ? [...images.slice(imageNum), ...images.slice(0, imageNum)]
            : images;

        // 파일 이름에서 전체 경로 제거하고 파일명만 사용
        const validImage = targetImages.find(img => {
            const ext = img.split('.').pop().toLowerCase();
            const fileName = img.split('/').pop(); // 파일명만 추출
            return image_ext.includes(ext) && fileName;
        });

        if (!validImage) {
            console.error('No valid image found in:', images);
            return null;
        }

        // 파일명만 추출
        const fileName = validImage.split('/').pop();
        
        // URL 생성
        return `/images/${folder_name}/${encodeURIComponent(fileName)}`;
    } catch (error) {
        console.error('Error in getImageUrl:', error);
        return null;
    }
}

//로컬 스토리지 토큰 삭제 로그아웃
	async function logout() {
		try {
			const response = await fetch('https://api2410.ebesesk.synology.me/auth/logout', {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${localStorage.getItem('access_token')}`
				}
			});

			if (response.ok) {
				localStorage.removeItem('access_token');
				window.location.href = '/login';
			} else {
				console.error('로그아웃 실패');
			}
		} catch (error) {
			console.error('로그아웃 중 오류 발생:', error);
		}
	}


// 페이지 변경 핸들러 수정
async function handlePageChange(newPage) {
    try {
        console.log('페이지 변경 시도:', newPage, '현재 페이지:', $currentPage, '전체 페이지:', totalPages);
        if (newPage >= 1 && newPage <= totalPages) {
            currentPage.set(newPage);
            await fetchGalleries(newPage);
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
    
    // 현재 이미지 인덱스 가져오기 (없으면 0으로 초기화)
    if (!currentImageIndexes[galleryIndex]) {
        currentImageIndexes[galleryIndex] = 0;
    }

    // 다음/이전 이미지 인덱스 계산
    if (direction === 'next') {
        currentImageIndexes[galleryIndex] = (currentImageIndexes[galleryIndex] + 1) % images.length;
    } else if (direction === 'prev') {
        currentImageIndexes[galleryIndex] = (currentImageIndexes[galleryIndex] - 1 + images.length) % images.length;
    }

    // 새 이미지 URL 가져오기
    const imageUrl = getImageUrl(gallery, currentImageIndexes[galleryIndex]);
    if (imageUrl) {
        const newImageUrl = await fetchData(imageUrl, { isImage: true });
        // imageUrls 스토어 업데이트
        imageUrls.update(urls => {
            const newUrls = [...urls];
            newUrls[galleryIndex] = newImageUrl;
						// $imageUrls[galleryIndex] = newImageUrl;
            return newUrls;
        });
    }
}

function exist_zip(images_name) {
	const zip_ext = ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'alz'];
	images_name = JSON.parse(images_name);
	// console.log('images_name:', images_name)
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
		console.log('folderStates:', $folderStates);
}

// 필터 적용
// applyFilter 함수 수정
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
        console.log('필터 적용 API 응답:', data);

        if (data) {
            galleries.set(data.items || []);
            // 전체 페이지 수 계산
            if (data.total_items) {
                totalPages = Math.ceil(data.total_items / pageSize);
            } else {
                totalPages = data.pages || Math.ceil(data.items.length / pageSize);
            }
            pageSize = data.size || 20;
            
            console.log('필터 적용 후 페이지 정보:', {
                currentPage: 1,
                totalPages,
                totalItems: data.total_items,
                pageSize,
                itemsCount: data.items.length
            });
            
            await fetchGalleryImages($galleries);
        }
    } catch (error) {
        console.error('갤러리 데이터를 불러오는데 실패했습니다:', error);
    }
}

	

// 검색어가 변경될 때마다 갤러리 데이터 다시 불러오기
$: if ($searchStore !== undefined) {
        handleSearch($searchStore);
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

				// 검색어가 있는 경우 추가
				if (searchTerm) {
						params.append('search', searchTerm);
				}

				// 활성화된 장르/폴더 추가
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
						
						console.log('검색 결과:', {
								searchTerm,
								totalItems: data.items.length,
								totalPages: data.pages
						});
						
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

	let sortType = 'id';
    
    async function handleSort(newSortType, orderType) {
        try {
            sortType = newSortType; // 현재 정렬 타입 업데이트
            
            const params = new URLSearchParams({
                page: $currentPage,
                size: pageSize,
                sort_by: newSortType,
                order: orderType
            });

            // 현재 검색어가 있다면 추가
            if ($searchStore) {
                params.append('search', $searchStore);
            }

            // 활성화된 장르/폴더 추가
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
	// 해당 버튼의 상태를 토글
	buttonStates[buttonNum - 1] = !buttonStates[buttonNum - 1];
	console.log(`버튼 ${buttonNum}: ${buttonStates[buttonNum - 1] ? 'ON' : 'OFF'}`);
}
	

	// 초기값 설정
	// galleries.set([]);
	// imageUrls.set([]);
	// currentPage.set(1);
	$: if ($searchStore !== undefined) {
        handleSearch($searchStore);
    }
  	
		// 초기 상태 설정
		$: if ($genres.length > 0 && Object.keys($folderStates).length === 0) {
			const initialStates = {};
			$genres.forEach(genre => {
					initialStates[genre] = false;
			});
			folderStates.set(initialStates);
	}

	onMount(async () => {
			try {
					await fetchGalleries($currentPage);
					await fetchRecommendations();
			} catch (error) {
					console.error('초기 데이터 로딩 실패:', error);
			}
	});
</script>





<!-- gallery-header 부분 수정 -->
<div class="gallery-header">
	<div class="button-container">
			<!-- 첫 번째 줄: 정렬 버튼들 -->
			<div class="button-row sort-buttons">
					<div class="spacer"></div> <!-- 왼쪽 공간을 채우는 요소 추가 -->
					<button 
							class="header-button {sortType === 'update_date' ? 'active' : ''}" 
							on:click={() => handleSort('update_date', 'desc')}
					>
							최신순
					</button>
					<button 
							class="header-button {sortType === 'rating' ? 'active' : ''}" 
							on:click={() => handleSort('rating', 'desc')}
					>
							평점순
					</button>
					<button 
							class="header-button {sortType === 'id' ? 'active' : ''}" 
							on:click={() => handleSort('id', 'desc')}
					>
							기본순
					</button>
			</div>

			<!-- 두 번째 줄: 장르 버튼들과 적용 버튼 -->
			<div class="button-row genre-buttons">
					<div class="spacer"></div> <!-- 왼쪽 공간을 채우는 요소 추가 -->
					{#each $genres as genre}
							<button 
									class="header-button {$folderStates[genre] ? 'active' : ''}" 
									on:click={() => toggleGenre(genre)}
							>
									{genre}
									<span class="status-indicator">
											{$folderStates[genre] ? 'ON' : 'OFF'}
									</span>
							</button>
					{/each}
					
					<button 
							class="header-button submit-button" 
							on:click={applyFilter}
					>
							적용
					</button>
			</div>
			<div>
				
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
<div 
    class="modal-backdrop" 
    on:click={closeModal}
    on:keydown={e => e.key === 'Escape' && closeModal()}
    role="dialog"
    aria-modal="true">
    <div 
        class="modal-content" 
        on:click|stopPropagation
        on:keydown|stopPropagation
        role="presentation">
        {#if $imageUrls[selectedIndex] && typeof $imageUrls[selectedIndex] === 'string'}
            <div class="modal-image-wrapper">
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
				<div class="gallery-item">
					<button class="image-button" on:click={() => openModal(i)}>
							<small>{gallery.folder_name.slice(0, 17)}</small>
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
								<a href="{'kddddds2://http://' + gallery.folder_name}" style="font-size: 0.9em;">
									<span class="average-rating">
											평균: {gallery.rating_average ? gallery.rating_average.toFixed(1) : '0.0'}
											⇒{JSON.parse(gallery.images_name).length}p
									</span>
								</a>
							{:else}
								<a href="{'kddddds2://http://'+ exist_zip(gallery.images_name)}" style="font-size: 0.9em;">
									<span class="average-rating">
											평균: {gallery.rating_average ? gallery.rating_average.toFixed(1) : '0.0'}
											⇒{JSON.parse(gallery.tags)['size']}		
										</span>
								</a>
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
			padding: 8px;  /* 패딩 줄임 */
			text-align: center;
			transition: transform 0.2s;
			max-width: 200px;  /* 개별 아이템 최대 너비 제한 */
			margin: 0 auto;  /* 중앙 정렬 */
	}

	.gallery-item img {
			width: 100%;
			aspect-ratio: 3/4;
			object-fit: cover;
			border-radius: 4px;
	}
	
	.gallery-item:hover {
			transform: scale(1.02);  /* 호버시 살짝 확대 */
	}

	.gallery-header {
        position: sticky;
        top: 0;
        background: white;
        padding: 0.5rem;
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

	.image-button {
        position: relative;  /* 추가 */
        width: 100%;
        padding: 0;
        border: none;
        background: none;
        cursor: pointer;
    }


    /* 선택사항: 영역을 시각적으로 확인하기 위한 스타일 */
    /* .left-area:hover, .right-area:hover {
        background-color: rgba(0, 0, 0, 0.1);
    } */

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
        top: 30px;          /* -40px에서 10px로 변경 */
        right: 30px;        /* 0에서 10px로 변경 */
        padding: 30px;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        border: none;
        cursor: pointer;
        z-index: 1001;      /* 이미지 위에 표시되도록 z-index 추가 */
        border-radius: 4px;  /* 선택적: 모서리를 둥글게 */
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
        /* height: 100%; */
        display: flex;
        align-items: center;
        opacity: 0;  /* 기본적으로 숨김 */
        transition: opacity 0.3s ease;  /* 부드러운 전환 효과 */
    }


    .modal-nav-button:hover {
        background: rgba(0, 0, 0, 0.7);  /* 버튼 호버링 시 더 진한 배경 */
    }

    .modal-nav-button.prev {
        left: 0;
    }

    .modal-nav-button.next {
        right: 0;
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
    /* ... 나머지 스타일 ... */
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
        display: inline-block;
        height: 100vh;  /* 추가: 뷰포트 높이만큼 설정 */
    }

    .modal-image {
        max-width: 50%;
        height: 100vh;  /* 수정: 뷰포트 높이로 설정 */
        object-fit: contain;  /* 이미지 비율 유지 */
        display: block;
        margin: 0 auto;
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
        z-index: 2;
    }

    .modal-nav-button.prev { left: 0; }
    .modal-nav-button.next { right: 0; }

    .modal-content {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 100vh;
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
</style>