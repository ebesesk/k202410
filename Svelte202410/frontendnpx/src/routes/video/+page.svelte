<script>
    import fastapi from "../../lib/api";
    import { page, keyword } from "../../lib/store"
    import Pagination from "./components/Pagination.svelte";
    
    // import Modal2 from '../../components/Modal2.svelte';
    import Modal2 from '../../components/video2.svelte';
    // import Info from "./components/Info.svelte";
    // import Scan from "./components/Scan.svelte";
    import Offcanvas from "./components/Offcanvas.svelte";
    import Info from "./components/Info.svelte"
    import SearchBoard from "./components/SearchBoard.svelte";
    // import env from 'meta'
    
    let video_list = []
    let size = 60
    let total = 0
    
    $: total_page = Math.ceil(total/size)    
    $: $page, $keyword, search_video()
    
    
    function search_video() {
      let params = {
        page: $page,
        size: size,
        keyword: $keyword
      }
      fastapi('get', '/api/video/search', params, (json) => {
        // console.log(json.video_list)
        video_list = json.video_list
        total = json.total
      })
    }
    
    function doVote(_video_id) {
      let url = "/api/video/vote"
      let params = {
        video_id: _video_id
      }
      fastapi('post', url, params,
        (json) => {
          search_video()
        },
        (err_json) => {
          error = err_json
        }
      )
    }
    
    function delVote(_video_id) {
      let url = "/api/video/delvote"
      let params = {
        video_id: _video_id,
      }
      fastapi('delete', url, params,
        (json) => {
          search_video()
        },
        (err_json) => {
          error = err_json
        }
      )
    }
    function doDislike(_video_id) {
      let url='/api/video/dislike'
      let params = {
        video_id: _video_id
      }
      fastapi('post', url, params,
        (json) => {
          search_video()
        },
        (err_json) => {
          error = err_json
        }
      )
    }
    
    function delDislike(_video_id) {
      let url = "/api/video/deldislike"
      let params = {
        video_id: _video_id
      }
      fastapi('delete', url, params,
        (json) => {
          search_video()
        },
        (err_jso) => {
          error = err_json
        }
      )
    }
    
    function toGif(video) {
      let _gif = encodeURIComponent("/video/" + 
                  video.dbid.substring(0,video.dbid.indexOf('/')+1) + 
                  'gif/' + video.dbid.substring(video.dbid.indexOf('/') + 1, 
                  video.dbid.lastIndexOf('.')) + ".gif")
      return _gif
    }
    function toWebp(video) {
      let _webp = encodeURIComponent("/video/" + 
                  video.dbid.substring(0,video.dbid.indexOf('/')+1) + 
                  'webp/' + video.dbid.substring(video.dbid.indexOf('/') + 1, 
                  video.dbid.lastIndexOf('.')) + ".webp")
      return _webp
    }
    function changeImage(video) {
      let image = document.getElementById(video.id)
      if (image.src.substring(image.src.lastIndexOf('.')+1) === 'gif') {
        image.src = toWebp(video)
      }else {
        image.src = toGif(video)
      }
    }
    
    
    let videoInfo
    let info
    function inputInfo(v) {
      videoInfo = v
    }
    
    // function doDislike() {
    //   pass
    // }
    // function delDislike() {
    //   pass
    // }
    </script>
    <div class="container"><SearchBoard/></div>
    
    
    
    <div class="col btn-offcanvas">
      <button class="btn btn-sm btn-light card-btn btn-offcanvas" 
              type="button" 
              data-bs-toggle="offcanvas" 
              data-bs-target="#offcanvasRight" 
              aria-controls="offcanvasWithBothOptions">SideMenu</button>
    </div>
    
    <Offcanvas/>
    
    <Modal2>
      <Info {videoInfo} bind:this={info}/>
    </Modal2>
    
    <div class="container-fluid ">
      <Pagination {size} {total} />
      <div class="row">
        {#each video_list as video}
    
        <div class="card px-0 mx-0 mb-3">
          <!-- <input type="checkbox" checked={yes}> -->
          <button class="btn btn-sm btn-light" on:click={changeImage(video)}>
            <img src="{toWebp(video)}" class="card-img-top" alt="..." id={video.id}>
          </button>
          <div class="card-body list-unstyled">
    
            <p class="card-text">
              {#if video.voter.length > 0}
              <button class="btn btn-sm btn-light card-btn" on:click="{delVote(video.id)}">
                <sapn class="badge rounded-pill bg-danger">{video.voter.length}</sapn>
              </button>
              {:else if video.dislike.length > 0}
              <button class="btn btn-sm btn-light card-btn" on:click="{delDislike(video.id)}">
                <sapn class="badge rounded-pill bg-dark">{video.dislike.length}</sapn>
              </button>
              {:else}
              <button class="btn btn-sm btn-light card-btn vote text-bg-danger" on:click="{doVote(video.id)}">Like</button>
              <button class="btn btn-sm btn-light card-btn vote text-bg-dark" on:click="{doDislike(video.id)}">Dis</button>
              {/if}
              
              
              <button type="button" 
                class="btn btn-light btn-sm card-btn text-bg-info" 
                data-bs-toggle="modal" 
                data-bs-target="#Modal"
                on:click={inputInfo(video)} 
              >Info</button>
              
              
                <a class="card-title" href="{'kddddds://http://' + video.dbid}">{video.dbid.substr(0,50)}</a>
              <!-- <h5 class="card-title">Card title</h5> -->
              <small>
                # {video.etc} # {video.width}x{video.height} 
                # {parseInt(video.showtime/60)}분{video.showtime%60}초
                # {parseInt(video.bitrate/1000)}kbps # {parseInt(video.filesize/1000000)}MB
              </small>
            </p>
          </div>
        </div>
        {/each}
      </div>
      <Pagination {size} {total} />
    </div>
      
      
    
    
    
    
    
    
    
    <!-- <Pagination {size} {total} /> -->
    
    
    
    
    
    <!-- <Modal2 {item}></Modal2> -->
    <!-- <Modal2 bind:this={modalInfo}>
      <Scan />
    </Modal2> -->
    
    
    
    
    <style>
    
    .col.btn-offcanvas {
      display: grid;
      /* justify-items: end; */
      justify-content: end;
      width: 100%;
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
    </style>