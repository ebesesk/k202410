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
	console.log('item:', item)
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
	console.log('url:', url)
	return url;
}


  // fetchImage 함수 수정
  async function fetchImage(items) {
		imageUrls.set(Array(items.length).fill().map(() => writable(null)));
		// console.log('imageUrls:', imageUrls)
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        console.error('인증 토큰이 없습니다.');
        window.location.href = '/login';
        return;
    }

    for (let i = 0; i < items.length; i++) {
			try {

				let _url = getImageUrl(items[i]);	
				// // console.log('folder_name:', items[i]['folder_name'])
				// let folder_name_arr = items[i]['folder_name'].split('/');
				// // console.log('folder_name_arr:', folder_name_arr)
				// // console.log('image_name:', image_name)
				// let folder_name = '';	
				// if (items[i]['folder_name'].includes('/')) {
				// 	for (let j = 0; j < folder_name_arr.length; j++) {
				// 		folder_name += encodeURIComponent(folder_name_arr[j]) + '/';
				// 	}
				// }else {
				// 	folder_name = encodeURIComponent(items[i]['folder_name']) + '/';
				// }

				// // console.log('items[i][images_name]:', items[i]['images_name'])
				// // console.log('images_name:',items[i]['images_name'])
				// let image_ext = ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'];
				// let images = JSON.parse(items[i]['images_name']);
				// // console.log('images:', images)
				// let file_name = '';
				// for (let j = 0; j < images.length; j++) {
				// 	let itemExt = images[j].split('.')[1].toLowerCase();
				// 	if (image_ext.includes(itemExt)) {
				// 		// console.log('itemExt:', itemExt)
				// 		// console.log('items[i][images_name][j]:', images[j])
				// 		file_name = encodeURIComponent(images[j]);
				// 		break;
				// 	}
				// }
		
										
				// console.log('folder_name + file_name:', folder_name + file_name)
				// let file_name = '1.png';
				// let _url = 'https://api2410.ebesesk.synology.me/images/' + folder_name + file_name;
				// console.log('_url:', _url)
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
					// imageUrls[i].set(url);
					$imageUrls[i] = url;
				} else {
					
					$imageUrls[i] = null;
				}
				
			} catch (error) {
				continue;
			}
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

function handleImageClick(i) {
        // 현재 페이지의 마지막 이미지인 경우
        if (i === $galleries.length - 1) {
            // 마지막 페이지가 아니면 다음 페이지로
            if ($currentPage < totalPages) {
                handlePageChange($currentPage + 1);
            }
        } else {
            // 다음 이미지로 스크롤
            const nextImage = document.querySelectorAll('.gallery-item')[i + 1];
            nextImage?.scrollIntoView({ behavior: 'smooth' });
        }
    }


	onMount(() => {
			fetchGalleries($currentPage);
	});
</script>





	<h1>갤러리 목록</h1>
	<Pagination
    currentPage={$currentPage}
    totalPages={totalPages}
    onPageChange={handlePageChange}
/>
	




<div class="gallery-container">
	<div class="galleries">
    {#each $galleries as gallery, i}
        <div class="gallery-item">
					{i + 1}. {(gallery.folder_name ?? '').slice(0, 10)}
					{#if $imageUrls[i] != null}
					<button class="image-button" on:click={() => handleImageClick(i)}>
						<img 
							src={$imageUrls[i]} 
							alt={gallery?.folder_name ?? ''} 
						/>
					</button>
					{:else}
                <p style="font-size: 0.9em;">이미지 로딩 중...</p>
            {/if}
            <p style="font-size: 0.9em;">{(gallery.file_date ?? '').slice(0, 10)}</p>
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
</style>