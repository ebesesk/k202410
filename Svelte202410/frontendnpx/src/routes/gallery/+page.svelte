<script>
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';  // writable import 추가
	import { galleries, imageUrls, currentPage } from '$lib/stores/galleryStore';
	import Pagination from '$lib/components/Pagination.svelte';
	
    

	// 전체 페이지 수 (서버에서 받은 총 아이템 수를 pageSize로 나눈 값)
	let totalPages = 1;
	// 한 페이지당 보여줄 갤러리 아이템 수 (API 요청 시 사용)
	let pageSize = 20;

		
	async function fetchGalleries(page) {

		try {
        const params = new URLSearchParams({
            page: page,
            size: pageSize,
            sort_by: 'id',
            order: 'desc'
        });
        
        // API 요청 시 인증 헤더 추가
        const accessToken = localStorage.getItem('accessToken');
        const response = await fetch(`https://api2410.ebesesk.synology.me/manga/mangas/?${params.toString()}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
				galleries.set(data.items);
				currentPage.set(data.page);
        // totalPages = data.total_pages;
        totalPages = data.pages;
        // totalPages = Math.ceil(data.total / data.size);
        pageSize = data.size;
        
        await fetchImage($galleries);
    } catch (error) {
        console.error('갤러리 데이터를 불러오는데 실패했습니다:', error);
        // 사용자에게 에러 메시지 표시
        // alert('갤러리 데이터를 불러오는데 실패했습니다. 다시 로그인해주세요.');
        // 로그인 페이지로 리다이렉트
        // window.location.href = '/login';
    }
}

// function handlePageChange(newPage) {
// 		if (newPage >= 1 && newPage <= totalPages) {
// 				fetchGalleries(newPage);
// 		}
// }



function getImageUrl(item, imageNum=false) {
	// console.log('item:', item)
	let folder_name_arr = item['folder_name'].split('/');
	let folder_name = '';
	for (let j = 0; j < folder_name_arr.length; j++) {
		folder_name += encodeURIComponent(folder_name_arr[j]) + '/';
	}
	let image_ext = ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'];
	let images = JSON.parse(item['images_name']);
	if (imageNum !== false) {
		images = images.slice(imageNum).concat(images.slice(0, imageNum));
	}
	let file_name = '';
	for (let j = 0; j < images.length; j++) {
		let itemExt = images[j].split('.')[1].toLowerCase();
		if (image_ext.includes(itemExt)) {
			file_name = encodeURIComponent(images[j]);
			break;
		}
	}

	let url = 'https://api2410.ebesesk.synology.me/images/' + folder_name + file_name;
	// console.log('url:', url)
	return url;
}


  // fetchImage 함수 수정
  async function fetchImage(items) {
		imageUrls.set(Array(items.length).fill().map(() => writable(null)));

    for (let i = 0; i < items.length; i++) {
			try {

				let _url = getImageUrl(items[i]);	
				
				$imageUrls[i] = await fetchImageData(_url);
				
			} catch (error) {
				continue;
			}
		}
}

async function fetchImageData(_url) {
	const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        console.error('인증 토큰이 없습니다.');
        window.location.href = '/login';
        return;
    }
	const response = await fetch(_url, {
		mode: "cors",
		headers: {
			"Authorization": `Bearer ${accessToken}`, 
			"Accept": "image/*"
		}
	});

	if (!response.ok) {
		throw new Error(`이미지 로딩 실패: ${response.status}`);
	}

	const blob = await response.blob();

	if (blob && blob.size > 0) {
		const url = URL.createObjectURL(blob);
		return url;
	} else {
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


	let imagesNum = Array($galleries.length).fill(0);	// 이미지 순서 변수
	async function handleImageClick(i, direction) {
		console.log('direction:', direction)
		console.log('i', i)
		if (direction === 'next') {
			if (JSON.parse($galleries[i].images_name).length-1 > imagesNum[i]) {
				imagesNum[i]++;
			}else {
				imagesNum[i] = 0;
			}
		}else if (direction === 'prev') {
			if (imagesNum[i] > 0) {
				imagesNum[i]--;
			}else {
				imagesNum[i] = JSON.parse($galleries[i].images_name).length-1;
			}
		}

		console.log('imagesNum[i]:', imagesNum[i])
		let url = getImageUrl($galleries[i], imagesNum[i]);
		console.log('url:', url)
		$imageUrls[i] = await fetchImageData(url);
		// openModal(i)
	}

	let selectedIndex = 0;
	let showModal = false;
    let selectedImage = '';

    function openModal(i) {

        selectedImage = $imageUrls[i];
				selectedIndex = i;
        showModal = true;
    }

    function closeModal() {
        showModal = false;
        selectedImage = '';
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


	onMount(() => {
			fetchGalleries($currentPage);
	});
</script>





	<!-- <h1>갤러리 목록</h1> -->
	<br>
	<Pagination
    currentPage={$currentPage}
    totalPages={totalPages}
    onPageChange={handlePageChange}
/>
	
{#if showModal}
<div class="modal-backdrop">
	<div class="modal-header">
			<h2 class="modal-title">{$galleries[selectedIndex].folder_name ?? ''}</h2>
	</div>
	<div class="modal-content">
		<img src={$imageUrls[selectedIndex]} alt="확대된 이미지" />
		<div class="left-area" 
		role="button"
		tabindex="0"
		on:click|stopPropagation={() => handleImageClick(selectedIndex, 'prev')}
		on:keydown|stopPropagation={e => e.key === 'Enter' && handleImageClick(selectedIndex, 'prev')}
		></div>
					<div class="right-area"
					role="button" 
					tabindex="0"
					on:click|stopPropagation={() => handleImageClick(selectedIndex, 'next')} 
					on:keydown|stopPropagation={e => e.key === 'Enter' && handleImageClick(selectedIndex, 'next')}
					></div>
        </div>
				<button class="close-button" on:click={closeModal}>닫기×</button>
			</div>
{/if}



<div class="gallery-container">
	<div class="galleries">
    {#each $galleries as gallery, i}
        <div class="gallery-item">
					<small 
						role="button"
						tabindex="0"
						on:click={() => openModal(i)}
						on:keydown={e => e.key === 'Enter' && openModal(i)}
					>{i + 1}. {(gallery.folder_name ?? '').slice(0, 15)}</small>
					{#if $imageUrls[i] && typeof $imageUrls[i] === 'string'}
					<button class="image-button">
						<img 
							src={$imageUrls[i]} 
							alt={gallery?.folder_name ?? ''} 
						/>
						<div class="left-area" 
							role="button" 
							tabindex="0" 
							on:click|stopPropagation={() => handleImageClick(i, 'prev')}
							on:keydown|stopPropagation={e => e.key === 'Enter' && handleImageClick(i, 'prev')}
						></div>
						<div class="right-area" 
							role="button" 
							tabindex="0" 
							on:click|stopPropagation={() => handleImageClick(i, 'next')}
							on:keydown|stopPropagation={e => e.key === 'Enter' && handleImageClick(i, 'next')}
						></div>
					</button>
					{:else}
                <p style="font-size: 0.9em;">이미지 로딩 중...</p>
            {/if}
						{#if exist_zip(gallery.images_name) === false}
							<a href="{'kddddds2://http://' + gallery.folder_name + '/' + exist_zip(gallery.images_name)}" style="font-size: 0.9em;">{(gallery.file_date ?? '').slice(0, 10)}</a>
						{:else}
							<a href="{'kddddds2://http://'+ gallery.folder_name + '/' + exist_zip(gallery.images_name)}" style="font-size: 0.9em;">{(gallery.file_date ?? '').slice(0, 10)}</a>
						{/if}
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

    .left-area, .right-area {
        position: absolute;
        top: 0;
        height: 100%;
        width: 50%;
        cursor: pointer;
    }

    .left-area {
        left: 0;
    }

    .right-area {
        right: 0;
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

    .modal-content {
        width: 200vw;         /* 90vw → 70vw로 축소 */
        height: 200vh;        /* 90vh → 80vh로 축소 */
        max-width: 1500px;   /* 최대 너비 제한 추가 */
        max-height: 1000px;   /* 최대 높이 제한 추가 */
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;   /* close 버튼 위치를 위해 */
    }

    .modal-content img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
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


		.modal-header {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1002;
    }

    .modal-title {
        color: white;
        font-size: 1em;
        text-align: center;
        margin: 0;
        padding: 10px;
        background-color: rgba(0, 0, 0, 0.7);
        border-radius: 5px;
        max-width: 80vw;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
</style>