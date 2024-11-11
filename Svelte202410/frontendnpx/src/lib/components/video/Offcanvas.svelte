<script>
  import fastapi from "$lib/api"
  import Scanfiles from "$lib/components/video/Scan.svelte";
  import Search from "$lib/components/video/Search.svelte"; 
  import Board from "$lib/components/video/Board.svelte";
  
  let menu1 = false
  let menu2 = false
  let menu3 =true
  </script> 
  
  
  
  <div class="offcanvas offcanvas-end" 
       tabindex="-1" id="offcanvasRight" 
       data-bs-scroll="true" 
       data-bs-backdrop="true"
       aria-labelledby="offcanvasRightLabel">
    <div class="offcanvas-header">
      <h5 id="offcanvasRightLabel">Offcanvas right</h5>
      <button type="button" class="btn-close text-reset" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body">
       
        <div class="col">
          <div class="btn-group">
              <button class="btn btn-light btn-sm" class:text-bg-dark={menu1}
              on:click={() => {menu1=true 
                               menu2=false
                               menu3=false}}>
              setup</button>
              <button class="btn btn-light btn-sm" class:text-bg-dark={menu2}
                on:click={() => {menu2=true 
                                 menu1=false
                                 menu3=false}}>
              파일</button>
              <button class="btn btn-light btn-sm" class:text-bg-dark={menu3}
                on:click={() => {menu3=true
                                 menu2=false 
                                 menu1=false}}>
                검색</button>
          </div>
        </div>
        <div class="col detail">
  
          {#if menu1}
            <Board />
          {/if}
  
          {#if menu2}
          <Scanfiles />
          {/if}
  
          {#if menu3}
          <Search />
          {/if}
  
      </div>
      
    </div>
  </div>
  
  <style>
  .col.detail {
    width: 100%;
  }
  .offcanvas.offcanvas-end {
      display: flex;
  }
  
  .offcanvas-body {
    font-size: small;
  }
  .btn {
    font-size: small;
  }
  </style>