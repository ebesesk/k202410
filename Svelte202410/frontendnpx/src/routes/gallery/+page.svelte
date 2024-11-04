<script>
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';  // writable import 추가
	import { galleries, imageUrls, currentPage } from '$lib/stores/galleryStore';
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
    const accessToken = localStorage.getItem('accessToken');
    
    if (!accessToken && !options.skipAuth) {
        console.error('인증 토큰이 없습니다.');
        window.location.href = '/login';
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

// 갤러리 데이터 가져오기
async function fetchGalleries(page) {
    try {
        const params = new URLSearchParams({
            page: page,
            size: pageSize,
            sort_by: 'id',
            order: 'desc'
        });

        const data = await fetchData(`/manga/mangas/?${params.toString()}`);
        galleries.set(data.items);
        currentPage.set(data.page);
        totalPages = data.pages;
        pageSize = data.size;
        
        await fetchGalleryImages($galleries);
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

            // 갤러리 데이터 새로고침 (평균 평점 업데이트를 위해)
            await fetchGalleries($currentPage);
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
// // 'curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJrZHMiLCJleHAiOjE3MzAxOTk5MDZ9.YIHf4Ob3a1KX7SF7aLwReTaVeAZ7FTySTJj8EjfTbe8" https://api2410.ebesesk.synology.me/images/1.png

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



async function handlePageChange(newPage) {
	$currentPage = newPage;
	await fetchGalleries(newPage);  // 새 갤러리 데이터 가져오기
	await fetchImage($galleries);  // 새 이미지 데이터 가져오기
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
	console.log('images_name:', images_name)
	for (let j = 0; j < images_name.length; j++) {
		for (let k = 0; k < zip_ext.length; k++) {
			if (images_name[j].endsWith(zip_ext[k])) {
				return images_name[j];
			}
			
		}
	}
	return false;
}




let searchTerm = '';
let searchTimeout;

	// 검색 함수 수정
	async function handleSearch() {
			try {
					const params = new URLSearchParams({
							page: 1,  // 검색 시 첫 페이지로 이동
							size: pageSize,
							sort_by: 'id',
							order: 'desc',
							search: searchTerm
					});

					const data = await fetchData(`/manga/mangas/?${params.toString()}`);
					galleries.set(data.items);
					currentPage.set(data.page);
					totalPages = data.pages;
					pageSize = data.size;
					
					await fetchGalleryImages($galleries);
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

		


	// 초기값 설정
	galleries.set([]);
	imageUrls.set([]);
	currentPage.set(1);

	onMount(async () => {
			try {
					await fetchGalleries($currentPage);
					await fetchRecommendations();
			} catch (error) {
					console.error('초기 데이터 로딩 실패:', error);
			}
	});
</script>





	<!-- <h1>갤러리 목록</h1> -->
	
	<Pagination
    currentPage={$currentPage}
    totalPages={totalPages}
    onPageChange={handlePageChange}
	/>

	
	
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




<!-- 추천 망가 섹션 추가 -->
<section class="recommended-section">
	<h2>추천 망가</h2>
	<div class="recommended-galleries">
			{#each $recommendedMangas as manga, i}
					<div class="gallery-item">
							<small>{manga.folder_name}</small>
							{#if $imageUrls[i] && typeof $imageUrls[i] === 'string'}
									<button class="image-button">
											<img src={$imageUrls[i]} alt={manga.folder_name} />
									</button>
							{:else}
									<p>이미지 로딩 중...</p>
							{/if}
							<div class="rating-container">
									<StarRating 
											value={$userRatings[manga.id] || 0}
											onChange={(rating) => rateGallery(manga.id, rating)}
									/>
									<span class="average-rating">평균: {manga.rating_average.toFixed(1)}</span>
							</div>
					</div>
			{/each}
	</div>
</section>

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
									</span>
								</a>
							{:else}
								<a href="{'kddddds2://http://'+ exist_zip(gallery.images_name)}" style="font-size: 0.9em;">
									<span class="average-rating">
											평균: {gallery.rating_average ? gallery.rating_average.toFixed(1) : '0.0'}
									</span>
								</a>
							{/if}

					</div>
				</div>
			{/each}
	</div>
</div>



<Pagination
    currentPage={$currentPage}
    totalPages={totalPages}
    onPageChange={handlePageChange}
/>






<style>
	.gallery-container {
		width: 100%;
		padding: 10px;
		box-sizing: border-box;
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



		.recommended-section {
        margin: 2rem 0;
        padding: 1rem;
        background: #f5f5f5;
        border-radius: 8px;
    }

    .recommended-galleries {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        padding: 1rem;
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
	
		
</style>