<script>
    import fastapi from "$lib/api";
    
    let scanInfo = {
      OverflowError: [],
      NotImplementedError: [],
      FileNotFoundError: [],
      알수없는에러: [],
      db_추가: [],
      converted: [],
      make_gif: [],
      make_webp: [],
      delete_gif:[],
      delet_webp: [],
      delet_dbids: [],
      detect_files: [],
    }
    
    function scan_files() {
        fastapi('get', '/video/scan_files', {}, (json) => {
            scanInfo = json
        })
    }
    
</script>
<span class="btn-span">
  <button class="btn btn-sm" on:click={scan_files}>파일정리</button>
</span>
<div class="text">
  ---------------------------------------------------------------------------------------<br>
  {#each Object.entries(scanInfo) as [k, v]}
  <b>{k} : {v.length}</b><br>  
  {#each v as k}
  {k}<br>
  {/each}
  ---------------------------------------------------------------------------------------<br>
  {/each}

</div>
    
<style>
div.text {
  font-size: x-small;
}
.btn-span {
  display: flex;
  flex-direction: row;
  justify-content: end; 
}
.btn {
  font-size: smaller;
}
</style>   
    