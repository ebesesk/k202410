<script>
  import 'bootstrap/dist/css/bootstrap.min.css';
  // import 'bootstrap';
  import fastapi from "$lib/api";
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { videoPage, keyword } from "$lib/stores/videoStore";
  import { userpoints, username, is_login } from "$lib/store";
  import Pagination from '$lib/components/video/Pagination.svelte'; // Pagination 컴포넌트 임포트
  import Modal2 from "$lib/components/video/video2.svelte";
  import Offcanvas from "$lib/components/video/Offcanvas.svelte";
  import Info from "$lib/components/video/Info.svelte";
  import SearchBoard from "$lib/components/video/SearchBoard.svelte";
  import { access_token } from '$lib/store';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store'; 

  let showSearchBoard = false;
  onMount(() => {
    if (browser) {
      if (!get(is_login)) {
          goto('/');
          return;
      }
      import('bootstrap');
      showSearchBoard = true;
      search_video();  // 초기 검색은 여기서 실행
      
      // 반응형 검색을 위한 구독 설정
      videoPage.subscribe(() => {
        if (browser) search_video();
      });
      
      keyword.subscribe(() => {
        if (browser) search_video();
      });
    }
  });
  

  let video_list = [];
  let size = 30;
  let total = 0;
  // let total_page = 0; // 전체 페이지 수를 저장할 변수
  let webpUrls = {};
  let gifUrls = {};

  let videoInfo;
  let info;
  function inputInfo(v) {
    // console.log('v', v)
    videoInfo = v;
  }

  $: total_page = Math.ceil(total / size);
  $: $videoPage, $keyword;

  
  // 비디오 검색 함수
  function search_video() {
    isLoading = true;
    let params = {
        page: $videoPage - 1,  // API 호출 시 현재 페이지에서 1을 빼서 전송
        size: size,
        keyword: JSON.stringify($keyword)
    };
    fastapi('get', '/video/search', params, (json) => {
        video_list = json.video_list;
        total = json.total;
        total_page = Math.ceil(total / size);

        video_list.forEach(video => {
            saveFetchImage(video);
            // fetchVideoRating(video.id); // 비디오 별점 가져오기
        });
    });
    
  }
  let isLoading = false;
  async function saveFetchImage(video) {
      isLoading = true;
      let webpUrl = toWebp(video.dbid);
      let gifUrl = toGif(video.dbid);
      webpUrls[video.id] = await fetchImage(webpUrl);
      gifUrls[video.id] = await fetchImage(gifUrl);
      isLoading = false;
  }

  function fetchImage(imgUrl) {
      if (imgUrl) {
          return new Promise((resolve, reject) => {
              fastapi('get', imgUrl, { isImage: true },
                  (url) => {
                      resolve(url);
                  },
                  (err) => {
                      console.error(`Error fetching image:`, err);
                      reject(err);
                  }
              );
          });
      }
  }

  function toGif(videodbid) {
      return '/videoimg/' + encodeURIComponent(videodbid.substring(0, videodbid.indexOf('/') + 1) + 'gif/' + videodbid.substring(videodbid.indexOf('/') + 1, videodbid.lastIndexOf('.')) + ".gif");
  }

  function toWebp(videodbid) {
      return '/videoimg/' + encodeURIComponent(videodbid.substring(0, videodbid.indexOf('/') + 1) + 'webp/' + videodbid.substring(videodbid.indexOf('/') + 1, videodbid.lastIndexOf('.')) + ".webp");
  }

  function changeImage(video) {
      let image = document.getElementById(video.id);
      if (image.src.substring(image.src.lastIndexOf('.') + 1) === 'gif') {
          image.src = webpUrls[video.id];
      } else {
          image.src = gifUrls[video.id];
      }
  }

  function handlePageChange(newPage) {
    // console.log("Page changed to:", newPage); // 디버깅용
    videoPage.set(newPage);
}

  let isOffcanvasOpen = false; // Offcanvas의 열림 상태를 관리하는 변수
  function toggleOffcanvas() {
      isOffcanvasOpen = !isOffcanvasOpen; // 상태를 반전시킴
  }



  let videoRatings = {}; // 비디오 별점을 저장할 객체
  let currentRating = {}; // 현재 선택된 비디오의 별점

  // 비디오 별점 가져오기
  async function fetchVideoRating(videoId) {
    fastapi('get', `/video/${videoId}/rating`, null,
    (json) => {
        // console.log('Success:', json.rating);
        currentRating[videoId] = json.rating
        // 성공 처리 
    },
    (error) => {
        console.error('Error:', error);
        // 실패 처리
    }
);
   }

  // 별점 수정 함수
  async function updateRating(videoId, rating) {
      await fastapi('post', `/video/${videoId}/rate`, { rating });
      currentRating[videoId] = rating; // 업데이트된 별점 저장
  }

  // 비디오 목록을 반복하면서 별점 가져오기
  // $: video_list.forEach(video => {
  //     // // currentRating이 undefined이거나 null일 경우에만 fetchVideoRating 호출
  //     // if (currentRating[video.id] === undefined || currentRating[video.id] === null) {
  //         fetchVideoRating(video.id);
  //     // }
  // });
  
  // video.dbid를 클릭할 때 조회수 증가
  const incrementViewCount = (videoId) => {
      fastapi('post', 
          `/video/${videoId}/view`, 
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

  {#if showSearchBoard && $is_login}
    <div class="container"><SearchBoard/></div>
  {/if}


{#if $username == 'kds'}
<div class="col btn-offcanvas">
  <button class="btn btn-sm btn-light card-btn btn-offcanvas float-end" 
          type="button" 
          data-bs-toggle="offcanvas" 
          data-bs-target="#offcanvasRight" 
          aria-controls="offcanvasWithBothOptions">SideMenu</button>
</div>

<Offcanvas/>
{/if}

<Modal2>
  <Info {videoInfo} bind:this={info}/>
</Modal2>


<div class="pagination-container">
  {#if total_page > 1}
    <Pagination 
      totalPages={total_page} 
      currentPage={$videoPage - 1} 
      on:pageChange={(e) => {
        handlePageChange(e.detail + 1);  // 이벤트로 받은 값에 1을 더해서 store에 저장
        search_video();
      }}
    />
  {/if}
</div>

<div class="container-fluid">
  <div class="row" style="display: flex; flex-wrap: wrap; justify-content: center;">
      {#each video_list as video}
      <div class="card" style="flex: 1 1 calc(100% - 10px); margin: 5px; max-width: 300px;">
          <button class="btn btn-sm btn-light" on:click={changeImage(video)}>
            {#if isLoading}
              <div class="d-flex justify-content-center align-items-center" style="height: 160px;">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">로딩중...</span>
                </div>
              </div>
            {:else}
              <img src="{webpUrls[video.id] || ''}" class="card-img-top" alt="..." id={video.id}>
            {/if}
          </button>
          <div class="card-body list-unstyled">
              <p class="card-text">
                  <button type="button" 
                    class="btn btn-light btn-sm card-btn text-bg-info"
                    data-bs-toggle="modal" 
                    data-bs-target="#Modal" 
                    on:click={() => inputInfo(video)}
                  >
                    보기
                  </button>
                  <span class="badge bg-danger ms-2">{Math.round(video.rating_average*10)/10}</span> <!-- 배지로 현재 평점 표시 -->
                  <select id="rating-{video.id}" bind:value={currentRating[video.id]} on:change={(e) => updateRating(video.id, e.target.value)} style="font-size: 0.75rem;">
                      <option value="0">0</option>
                      <option value="1">1</option>
                      <option value="2">2</option>
                      <option value="3">3</option>
                      <option value="4">4</option>
                      <option value="5">5</option>
                  </select>
                  <a class="card-title" href="{'kddddds://http://' + video.dbid}"
                    on:click={() => incrementViewCount(video.id)} >
                    {video.dbid.substr(0, 50)}
                  </a>
                  <small>
                      # {video.etc} # {video.width}x{video.height} 
                      # {parseInt(video.showtime / 60)}분{video.showtime % 60}초
                      # {parseInt(video.bitrate / 1000)}kbps # {parseInt(video.filesize / 1000000)}MB
                  </small>
              </p>
          </div>
      </div>
      {/each}
  </div>
</div>

<style>
  	.pagination-container {
        display: flex;
        justify-content: center;  /* 가운데 정렬 */
        align-items: center;
        width: 100%;
        padding: 1rem 0;
        margin: 1rem 0;
    }
.container-fluid {
  justify-content: center;
  padding: 0x;
  margin: 0;
  /* padding-left: 15px; */
  /* margin-right: auto; */
  /* margin-left: auto; */
}
.row {
  /* width: 100%; */
  padding: 0;
  margin: 0;
  justify-content: center;
  justify-self: center;
}
/* .card.border-danger {
  border: 1;
} */
.card {
  width: 18rem;
  /* width: 0px; */
  /* margin: 0; */
  padding-left: 1px;
  /* height: 100%; */
  border: 0;
}
.card-img-top {
  width: 100%;
  height: 160px;
  object-fit: contain;
}
.card-title {
  font-size: smaller;
}
.card-text {
  font-size: smaller;
  line-height: 1.3;
}
.card-btn {
  font-size: xx-small;
  --bs-btn-padding-y: .01rem; 
  --bs-btn-padding-x: .5rem; 
  --bs-btn-font-size: .75rem;
  /* height: ; */
}
/* .card-boy {
  padding: 0%;
} */
/* .voter {
  background-color: rgb(235, 205, 205);
  border-color: crimson;
  
} */
/* .dislike {
} */
  
  select {
    margin-left: 10px;
}
  


</style>
