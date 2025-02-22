<script>
    import fastapi from "$lib/api"
    import { videoPage, keyword } from "$lib/stores/videoStore"
    
    
    let none
    let keywords = []
    let video = {
      resolution: [],
      display_quality: [],
      country: [],
      face: [],
      look: [],
      age: [],
      pussy: [],
      etc: "",
      
    }
    
  
    function onSearch() {
      let video_json = video
      // let video_json = JSON.parse(video)
      console.log('video_json', video_json)
      $keyword = video_json
      $videoPage = 0
    }
    
    function allSelect() {
      video = {
        resolution: ["high","middle","low"],
        display_quality: ["아주좋음","좋음","보통","흐릿","폐기"],
        country: ["한국","일본","중국","서양","기타"],
        face: ["선명","흐릿"],
        look: ["마름","보통","뚱"],
        age: ["어림","학생","아가씨","아줌마","나이많음"],
        pussy: ["선명","흐릿"],
        etc: ""
      }
    }
    function allUnselect() {
      video = {
        resolution: [],
        display_quality: [],
        country: [],
        face: [],
        look: [],
        age: [],
        pussy: [],
        etc: ""
      }
    }

function get_keywords() {
  fastapi ('get', '/video/keywords', {}, (json) => {
    keywords = json.keywords
    keywords = JSON.stringify(keywords).split(',')
    console.log(keywords)
  })
}
  </script>
<div class="container"> 
    <!-- <div >
      <input type="text" class="form-control-sm"  bind:value="{kw}">
      <button class="btn btn-primary"  on:click={() => {$keyword = kw, $page = 0}}>검색</button>
    </div> -->
    <div class="select" >
      <div class="top-button">
        <button class="btn btn-outline-dark btn-sm" on:click={allSelect} >선택</button>
        <button class="btn btn-outline-dark btn-sm" on:click={allUnselect} >해제</button>
      </div>
      <div class="etc-form">
        <form on:submit|preventDefault={onSearch}>
          <label>
            ect: <input type="text" bind:value={video.etc}>
          </label>
        </form>
        <button on:click={() => {video.etc=""}} class="btn btn-light btn-sm">C</button>
        <button on:click={() => {video.etc="#not, test2"}} class="btn btn-light btn-sm">T</button>
        <button on:click={() => {video.etc="test2"}} class="btn btn-light btn-sm">t</button>
        <button class="btn btn-outline-dark btn-sm" on:click={onSearch}>검색</button>
      </div>
      <p class="get-keywords">
        <b>검색어, #not, 검색</b> 
        <button class="btn btn-outline-dark btn-sm" on:click={get_keywords}>Get Keyword</button>
        <br>
        {#each keywords as keyword} {keyword},&nbsp; {/each} 
      </p>

      <div>
        해상도:
        <label>
          <input type="checkbox" class="form-check-input text-danger" bind:group={video.resolution} value="high" >고
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.resolution} value="middle">중
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.resolution} value="low">저
        </label>
        <label class="text-danger font-weight-bold">
          <input type="checkbox" class="form-check-input" bind:group={video.resolution} value="not">not
        </label>
        <button on:click={() => {video.resolution=['high', 'middle', 'low']}} class="btn btn-light btn-sm">S</button>
        <button on:click={() => {video.resolution=[]}} class="btn btn-light btn-sm">C</button>
      </div>
      <div class="display_quality">
        화질:
          <label>
            <input type="checkbox" class="form-check-input" bind:group={video.display_quality} value="아주좋음" >아주좋음
          </label>
          <label>
            <input type="checkbox" class="form-check-input" bind:group={video.display_quality} value="좋음">좋음
          </label>
          <label>
            <input type="checkbox" class="form-check-input" bind:group={video.display_quality} value="보통">보통
          </label>
          <label>
            <input type="checkbox" class="form-check-input" bind:group={video.display_quality} value="흐릿">흐릿
          </label>
          <label>
            <input type="checkbox" class="form-check-input" bind:group={video.display_quality} value="폐기">폐기
          </label>
          <label class="text-danger font-weight-bold">
            <input type="checkbox" class="form-check-input" bind:group={video.display_quality} value="not">not
          </label>
          <button on:click={() => {video.display_quality=['아주좋음', '좋음', '보통', '흐릿', '폐기']}} class="btn btn-light btn-sm">S</button>
          <button on:click={() => {video.display_quality=[]}} class="btn btn-light btn-sm">C</button>
      </div>
      <div class="country">
        국가:
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.country} value="한국" >한국
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.country} value="일본">일본
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.country} value="중국">중국
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.country} value="서양">서양
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.country} value="기타">기타
        </label>
        <label class="text-danger font-weight-bold">
          <input type="checkbox" class="form-check-input" bind:group={video.country} value="not">not
        </label>
        <button on:click={() => {video.country=['한국', '일본', '중국', '서양', '기타']}} class="btn btn-light btn-sm">S</button>
        <button on:click={() => {video.country=[]}} class="btn btn-light btn-sm">C</button>
      </div>
      <div>
        얼&nbsp;&nbsp;굴:
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.face} value="선명" >선명
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.face} value="흐릿">흐릿
        </label>
        <label class="text-danger font-weight-bold">
          <input type="checkbox" class="form-check-input" bind:group={video.face} value="not">not
        </label>
        <button on:click={() => {video.face=['선명', '흐릿']}} class="btn btn-light btn-sm">S</button>
        <button on:click={() => {video.face=[]}} class="btn btn-light btn-sm">C</button>
      </div>
      <div>
        외&nbsp;&nbsp;모:
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.look} value="마름">마름
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.look} value="보통">보통
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.look} value="뚱">뚱
        </label>
        <label class="text-danger font-weight-bold">
          <input type="checkbox" class="form-check-input" bind:group={video.look} value="not">not
        </label>
        <button on:click={() => {video.look=['마름', '보통', '뚱']}} class="btn btn-light btn-sm">S</button>
        <button on:click={() => {video.look=[]}} class="btn btn-light btn-sm">C</button>
      </div>
      <div class="age">
        나이:
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.age} value="어림" >어림
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.age} value="학생">학생
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.age} value="아가씨">아가씨
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.age} value="아줌마">아줌마
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.age} value="나이많음">많음
        </label>
        <label class="text-danger font-weight-bold">
          <input type="checkbox" class="form-check-input" bind:group={video.age} value="not">not
        </label>
          <button on:click={() => {video.age=['어림', '학생', '아가씨', '아줌마', '나이많음']}} class="btn btn-light btn-sm">S</button>
          <button on:click={() => {video.age=[]}} class="btn btn-light btn-sm">C</button>
      </div>
      <div>
        ㅂ&nbsp;&nbsp;ㅈ:
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.pussy} value="선명" >선명
        </label>
        <label>
          <input type="checkbox" class="form-check-input" bind:group={video.pussy} value="흐릿">흐릿
        </label>
        <label class="text-danger font-weight-bold">
          <input type="checkbox" class="form-check-input" bind:group={video.pussy} value="not">not
        </label>
        <button on:click={() => {video.pussy=['선명', '흐릿']}} class="btn btn-light btn-sm">S</button>
        <button on:click={() => {video.pussy=[]}} class="btn btn-light btn-sm">C</button>
      </div>
    </div>
      
      
      
      
      
      
      
    <div class="row-check" >
      <div class="col radio-c" >
        <label>
          <input type="radio" name="school_uniform" bind:group={video.school_uniform} value={true}>교복 
        </label><br>
        <label class="text-danger font-weight-bold">
          <input type="radio" name="school_uniform" bind:group={video.school_uniform} value = {false}>교복 
        </label>
      </div>
      <div class="col radio-c">
        <label>
          <input type="radio" name='hip' bind:group={video.hip} value={true}>hip 
        </label><br>
        <label class="text-danger font-weight-bold">
          <input type="radio" name='hip' bind:group={video.hip} value={false}>hip 
        </label>
      </div>
      <div class="col radio-c">
        <label>
          <input type="radio" name='group' bind:group={video.group} value={true}>그룹
        </label><br>
        <label class="text-danger font-weight-bold">
          <input type="radio" name='group' bind:group={video.group} value={false}>그룹 
        </label>
      </div>
      <div class="col radio-c">
        <label>
          <input type="radio" name='pregnant' bind:group={video.pregnant} value={true}>임신 
        </label><br>
        <label class="text-danger font-weight-bold">
          <input type="radio" name='pregnant' bind:group={video.pregnant} value={false}>임신 
        </label>
      </div>
      <div class="col radio-b">
        <button on:click={() => {video.school_uniform = none
                                  video.hip = none
                                  video.group = none
                                  video.pregnant = none
                                }} class="btn btn-light btn-sm">
          C</button>
        </div>
      </div>
      
        
        
        
      <div class="row-check" >
        <div class="col radio-c">
          <label>
            <input type="radio" name='conversation' bind:group={video.conversation} value={true}>대화 
          </label><br>
          <label class="text-danger font-weight-bold">
            <input type="radio" name='conversation' bind:group={video.conversation} value={false}>대화
          </label>
        </div>
        <div class="col radio-c">
          <label>
            <input type="radio" name='lesbian' bind:group={video.lesbian} value={true}>레즈
          </label><br>
          <label class="text-danger font-weight-bold">
            <input type="radio" name='lesbian' bind:group={video.lesbian} value={false}>레즈 
          </label>
          <!-- <label class="text-danger font-weight-bold">
            <input type="radio" name='lesbian' group={video.lesbian} value={none}>레&nbsp;&nbsp;즈 
          </label> -->
        </div>
        <div class="col radio-c">
          <label>
            <input type="radio" name='ani' bind:group={video.ani} value={true}>에니
          </label><br>
          <label class="text-danger font-weight-bold">
            <input type="radio" name='ani' bind:group={video.ani} value={false}>에니
          </label>
        </div>
        <div class="col radio-c">
          <label>
            <input type="radio" name='oral' bind:group={video.oral} value={true}>입&nbsp;&nbsp;&nbsp;&nbsp; 
          </label><br>
          <label class="text-danger font-weight-bold">
            <input type="radio" name='oral' bind:group={video.oral} value={false}>입&nbsp;&nbsp;&nbsp;&nbsp; 
          </label>
        </div>
        <div class="col radio-b">
          <button on:click={() => {video.conversation = none
                                  video.lesbian = none
                                  video.ani = none
                                  video.oral = none
                                }} class="btn btn-light btn-sm">
          C</button>
        </div>
    </div>

    
    <div class="row-check">
      <div class="col radio-c">
        <label>
          <input type="radio" name='masturbation' bind:group={video.masturbation} value={true}>자위 
        </label><br>
        <label class="text-danger font-weight-bold">
          <input type="radio" name='masturbation' bind:group={video.masturbation} value={false}>자위 
        </label>
      </div>
      <div class="col radio-c">
        <label >
          <input type="radio" name='massage' bind:group={video.massage} value={true}>마사지 
        </label><br>
        <label class="text-danger font-weight-bold" >
          <input type="radio" name='massage' bind:group={video.massage} value={false}>마사지 
        </label>
      </div>
      <div class="col radio-c">
        <label>
          <input type="radio" name='uniform' bind:group={video.uniform} value={true}>회사 
        </label><br>
        <label class="text-danger font-weight-bold">
          <input type="radio" name='uniform' bind:group={video.uniform} value={false}>회사 
        </label>
      </div>
      <div class="col radio-c">
        <label >
          <input type="radio" name='family' bind:group={video.family} value={true}>family 
        </label><br>
        <label class="text-danger font-weight-bold" >
          <input type="radio" name='family' bind:group={video.family} value={false}>family 
        </label>
      </div>
      <div class="col radio-b">
        <button class="btn btn-light btn-sm" 
        on:click={() => {video.masturbation = none
                         video.massage = none
                         video.uniform = none
                         video.family = none}}>
          C</button>
        </div>
      </div>
      
        
        
        
        
        
        
        
        
        
      <div class="row">
        <div class="col">
          <label >
            <input type="radio" name="ad_start" bind:group={video.ad_start} value="{true}"/>광고
          </label> 
          <label class="text-danger font-weight-bold" >
            <input type="radio" name="ad_start" bind:group={video.ad_start} value="{false}"/>광고
          </label>
          <button class="btn btn-light btn-sm" on:click={() => {video.ad_start = none}} >C</button>
        </div>
        <div class="col" >
          별점 : 
          <select bind:value={video.star}>
            <option value={none}></option>
            <option value={null}>None</option>
            <option value={true}>all</option>
            <option value="1">♥</option>
            <option value="2">♥♥</option>
            <option value="3">♥♥♥</option>
            <option value="4">♥♥♥♥</option>
            <option value="5">♥♥♥♥♥</option>
          </select>
          <b class="text-danger">{"♥".repeat(video.star)}</b> 
        </div>
      </div>

      <div>
        <label>
          <input type="radio" name='vote' bind:group={video.vote} value={true}>Vote
        </label>
        <button class="btn btn-light btn-sm" on:click={() => {video.vote = none}} >C</button>
        <label>
          <input type="radio" name='dislike' bind:group={video.dislike} value={true}>Dislike
        </label>
        <button class="btn btn-light btn-sm" on:click={() => {video.dislike = none}} >C</button>
        <label>
          <input type="radio" name='dislike' bind:group={video.random} value={true}>Random
        </label>
        <button class="btn btn-light btn-sm" on:click={() => {video.random = none}} >C</button>
      </div>
  
  
  
  
</div>

  



<style>
.container {
  display: flex;
  flex-direction: column;
  font-size: 9px;
  justify-content: space-between;
  width: 100%;
  height: 400px;
}
button {
  justify-items: center;
  font-size: smaller;
}
.etc-form {
  display: flex;
  flex-direction: col;
}
.display_quality {
  font-size: smaller;
}
.country {
  font-size: smaller;
}
.age {
  display: flex;
  /* justify-content: end; */
}
.row-check {
  display: flex;
  flex-direction: row;
  justify-content: left;
  height: 400px;
  width: 80%;
}
.select {
  display: flex;
  flex-direction: column;
  justify-content:space-between;
  align-content: center;
}
.top-button {
  display: flex;
  justify-content: end;
}
.top-button > button {
  font-size: smaller;
}
button {
  font-size: 9px;
  padding: 3px;
  margin: 3px;
}
label {
  font-size: 9px;
}
</style>
