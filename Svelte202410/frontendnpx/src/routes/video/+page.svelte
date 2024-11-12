<script>
  import 'bootstrap/dist/css/bootstrap.min.css';
  import 'bootstrap';
  import fastapi from "$lib/api";
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { videoPage, keyword } from "$lib/stores/videoStore";
  import Pagination from '$lib/components/video/Pagination.svelte'; // Pagination 컴포넌트 임포트
  import Modal2 from "$lib/components/video/video2.svelte";
  import Offcanvas from "$lib/components/video/Offcanvas.svelte";
  import Info from "$lib/components/video/Info.svelte";
  import SearchBoard from "$lib/components/video/SearchBoard.svelte";

  let video_list = [];
  let size = 30;
  let total = 0;
  // let total_page = 0; // 전체 페이지 수를 저장할 변수
  let webpUrls = {};
  let gifUrls = {};

  let videoInfo;
  let info;

  function inputInfo(v) {
    videoInfo = v
  }

  $: total_page = Math.ceil(total / size);
  $: $videoPage, $keyword, search_video();

  // 비디오 검색 함수
  function search_video() {
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
        });
    });
  }

  async function saveFetchImage(video) {
      let webpUrl = toWebp(video.dbid);
      let gifUrl = toGif(video.dbid);
      webpUrls[video.id] = await fetchImage(webpUrl);
      gifUrls[video.id] = await fetchImage(gifUrl);
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
    console.log("Page changed to:", newPage); // 디버깅용
    videoPage.set(newPage);
}

  let isOffcanvasOpen = false; // Offcanvas의 열림 상태를 관리하는 변수
  function toggleOffcanvas() {
      isOffcanvasOpen = !isOffcanvasOpen; // 상태를 반전시킴
  }

  onMount(() => {
      if (browser) {
          const token = localStorage.getItem('accessToken');
          if (!token) {
              window.location.href = '/';
              return;
          }
          search_video(); // 초기 비디오 검색
      }
  });
</script>

<div class="container"><SearchBoard/></div>



<div class="col btn-offcanvas">
  <button class="btn btn-sm btn-light card-btn btn-offcanvas float-end" 
          type="button" 
          data-bs-toggle="offcanvas" 
          data-bs-target="#offcanvasRight" 
          aria-controls="offcanvasWithBothOptions">SideMenu</button>
</div>

<Offcanvas/>

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
              <img src="{webpUrls[video.id] || ''}" class="card-img-top" alt="..." id={video.id}>
          </button>
          <div class="card-body list-unstyled">
              <p class="card-text">
                  <button type="button" class="btn btn-light btn-sm card-btn text-bg-info" on:click={inputInfo(video)}>Info</button>
                  <a class="card-title" href="{'kddddds://http://' + video.dbid}">{video.dbid.substr(0, 50)}</a>
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
  .card {
    width: 100%; /* 카드의 너비를 100%로 설정 */
    max-width: 300px; /* 카드의 최대 너비를 설정 */
    /* 필요에 따라 높이 조정 가능 */
  }
  .card-img-top {
    width: 100%;
    height: auto; /* 높이를 자동으로 조정하여 비율 유지 */
    object-fit: cover; /* 이미지 비율 유지 */
  }

  .offcanvas {
      position: fixed; /* 고정 위치로 설정 */
      top: 0;
      right: 0; /* 우측에서 나오도록 설정 */
      width: 450px; /* 원하는 너비 설정 */
      height: 100%; /* 전체 높이 사용 */
      background-color: white; /* 배경색 설정 */
      transition: transform 0.3s ease; /* 애니메이션 효과 */
      transform: translateX(100%); /* 기본적으로 화면 밖에 위치 */
      z-index: 1050; /* 다른 요소 위에 표시 */
  }

  .offcanvas.open {
      transform: translateX(0); /* 열릴 때 화면 안으로 이동 */
  }
</style>

