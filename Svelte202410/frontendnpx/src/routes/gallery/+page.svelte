<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Pagination from '$lib/components/Pagination.svelte';

	let galleries = [];
	let currentPage = 1;
	let totalPages = 1;
	let pageSize = 20;

		
	async function fetchGalleries(page) {
		console.log('fetchGalleries:', page)
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
        console.log('받아온 데이터:', data);
        
        galleries = data.items;
        totalPages = Math.ceil(data.total / data.size);
        currentPage = data.page;
        pageSize = data.size;
        
        await fetchImage(galleries);
    } catch (error) {
        console.error('갤러리 데이터를 불러오는데 실패했습니다:', error);
        // 사용자에게 에러 메시지 표시
        alert('갤러리 데이터를 불러오는데 실패했습니다. 다시 로그인해주세요.');
        // 로그인 페이지로 리다이렉트
        // window.location.href = '/login';
    }
}

function handlePageChange(newPage) {
		if (newPage >= 1 && newPage <= totalPages) {
				fetchGalleries(newPage);
		}
}



  // 이미지 URL을 저장할 배열 추가
  let imageUrls = [];

  // fetchImage 함수 수정
  async function fetchImage(items) {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        console.error('인증 토큰이 없습니다.');
        window.location.href = '/login';
        return;
    }

    for (let i = 0; i < items.length; i++) {
        try {
            let image_name = JSON.parse(items[i]['images_name'])[0];
						let folder_name_arr = items[i]['folder_name'].split('/');
						console.log('folder_name_arr:', folder_name_arr)
						console.log('image_name:', image_name)
						let folder_name = '';	
						for (let j = 0; j < folder_name_arr.length; j++) {
							folder_name += encodeURIComponent(folder_name_arr[j]) + '/';
						}
            let file_name = encodeURIComponent(image_name);
						console.log('folder_name + file_name:', folder_name + file_name)
						// let file_name = '1.png';
            let _url = 'https://api2410.ebesesk.synology.me/images/' + folder_name + file_name;
            console.log('_url:', _url)
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
            imageUrls[i] = URL.createObjectURL(blob);
            
        } catch (error) {
            console.error(`이미지 ${i} 로딩 중 에러:`, error);
            imageUrls[i] = null; // 에러 발생 시 null 설정
        }
    }
}


  // galleries가 변경될 때마다 이미지 URL 업데이트
  $: {
    if (galleries.length > 0) {
      Promise.all(galleries.map((_, i) => fetchImage(i)))
        .then(urls => {
          imageUrls = urls;
        });
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






	onMount(() => {
			fetchGalleries(1);
	});
</script>

<!-- 로그아웃 버튼 -->
<button on:click={logout}>로그아웃</button>
<button on:click={() => goto('/')}>처음으로</button>
<button on:click={fetchGalleries}>갤러리 불러오기</button>




	<h1>갤러리 목록</h1>
	<Pagination
    currentPage={currentPage}
    totalPages={totalPages}
    onPageChange={handlePageChange}
/>
	




<div class="gallery-container">
	<div class="galleries">
			{#each galleries as gallery, i}
					<div class="gallery-item">
							{i + 1}. {gallery.folder_name.slice(0, 10)}
							{#if imageUrls[i]}
									<img src={imageUrls[i]} alt={gallery.folder_name} />
							{:else}
									<p style="font-size: 0.9em;">이미지 로딩 중...</p>
							{/if}
							<p style="font-size: 0.9em;">{gallery.file_date.slice(0, 10)}</p>
					</div>
			{/each}
	</div>
</div>



<Pagination
    currentPage={currentPage}
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
</style>