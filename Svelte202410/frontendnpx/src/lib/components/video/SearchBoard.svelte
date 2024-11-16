<script>
    import fastapi from "$lib/api";
    import {userpoints, username, is_login} from "$lib/store"
    import { videoPage, keyword } from "$lib/stores/videoStore";
    import moment from "moment";
    import { onMount } from 'svelte';
    // import { browser } from '$app/environment';
    moment.locale('ko')
    
    // const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    // const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    
    let tooltipList = [];
    // let subject;
    // let content;
    // let query = "";
    // let question_list = [];

    onMount(async () => {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
        
        if ($is_login) {
            await get_question_list();  // onMount에서만 호출
        }
    });





    // export let onSearch
    let subject;
    let content;
    
    function post_question(event) {
      event.preventDefault()
      let url = "/question/create"
      // console.log('subject', subject)
      // console.log('content', content)
      let params = {
          subject: '#쿼리#' + subject,
          content: content,
      }
      fastapi('post', url, params,
          (json) => {
              get_question_list()
          },
          (json_error) => {
          error = json_error
          }
        )
      }
    
    function get_question_list() {
      let url = "/question/list"  
      let params = {
        page: 0,
        size: 50,
        keyword: '#쿼리#'
      }
      fastapi('get', url, params, (json) => {
        question_list = json.question_list
        
        // console.log(question_list)
        // console.log(question_list[0])
        }
      )
    } 
    function update_question(event) {
      event.preventDefault()
      let url = "/question/update"
      let params = {
        question_id: question_id,
        subject: subject,
        content: content
      }
      fastapi('put', url, params, 
        (json) => {
          get_question_list()
        },
        (json_error) => {
          error = json_error
        }
      )
    }
    
    function delete_question(_question_id) {
      if(window.confirm('정말로 삭제하시겠습니까?')) {
        let url = "/question/delete"
        let params = {
          question_id: _question_id
        }
        fastapi('delete', url, params, 
          (json) => {
            get_question_list()    
          },
          (err_json) => {
              error = err_json
          }
        )
      }  
    }
    let query = ""
    let question_list = []
    get_question_list()
    // console.log(question_list)
    
    
    function etcToString(q) {
      if (Object.keys(q).includes('etc') && q['etc'].length > 0) {
        let _etc = q.etc.filter(value => value !== '')
        _etc = q.etc.join(',')
        q.etc = _etc
        // console.log('q', q)
        return q
      }else {
        return q
      }
    }
    
    function runQuery(_query) {
      query = _query
      let q = _query.replace(/'/gi, '"').replaceAll('True', 'true').replaceAll('False', 'false')
      etcToString(JSON.parse(q))
      q = etcToString(JSON.parse(q))
      $videoPage = 0
      // $keyword = JSON.stringify(q)
      $keyword = q
    }
    </script>
    {#if $username == 'kds'}
    <div class="row up">
      <div class="col">
        <div class="input-group input-group-sm pt-1 maker">
          <p>{query}</p>
          <textarea type="txt" class="form-control-sm"  bind:value={subject} placeholder="제목" rows="1" cols=25></textarea>
          <!-- <textarea class="form-control-sm" bind:value={content} rows="1" cols="38"></textarea> -->
          <textarea class="form-control-sm" bind:value={content} rows="1" cols="38"></textarea>
          <button class="btn btn-sm text-bg-primary" on:click={post_question}>작성</button>
        </div>
      </div>
    </div>
    {/if}
      
    
    <div class="row pt-1">
      {#if $username == 'kds'}
      {#each question_list as question, index}
      {#if question.subject.startsWith('#쿼리#')}
      <div class="col content">
        <button type="button" class="btn btn-outline-dark subject" on:click={() => {runQuery(question.content)}}>
            <b>{question.subject.replace('#쿼리#', '')}</b>
        </button>
        <button class="badge text-bg-danger bg-sm del" on:click={delete_question(question.id)}>D</button>
      </div>
      {/if}
      {/each}
      {/if}

      {#if $username != 'kds'}
      {#each [{content:"{'etc':['test2']}", subject:'test'}] as question, index}
      <div class="col content">
        <button type="button" class="btn btn-outline-dark subject" on:click={() => {runQuery(question.content)}}>
            <b>{question.subject.replace('#쿼리#', '')}</b>
        </button>
        <button class="badge text-bg-danger bg-sm del" on:click={delete_question(question.id)}>D</button>
      </div>
      {/each}
      {/if}
    </div>  
    
    
    
    
    
    
    
    <style>
    .input-group > p {
      font-size: xx-small;
    }
    textarea {
      font-size: small;
    }
    .row.up {
      display: flex;
      flex-flow: row;
      font-size: small;
    }
    .row.pt-1 {
      display: flex;
      justify-items: auto;
      font-size: xx-small;
    }
    .maker {
      justify-content: end;
    }
    .col.content {
      display: flex;
      white-space: nowrap;
      font-size: xx-small;
    }
    .subject {
      font-weight: bold;
      font-size: smaller;
      white-space: nowrap;
      align-self: center;
      /* width: 100%; */
    }
    .badge.del {
      font-size: xx-small;
      justify-self: end;
      align-self:baseline;
      cursor: pointer;
      
    }
    /* button.badge {
      font-size: xx-small;
    } */
    </style>