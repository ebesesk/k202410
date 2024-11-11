<script>
    import { createEventDispatcher, onDestroy } from 'svelte';
    import { clickOutside } from '$lib/clickOutside';
    
    const previously_focused = typeof document !== 'undefined' && document.activeElement;
    
      if (previously_focused) {
      onDestroy(() => {
        previously_focused.focus();
          });
      }
       
  
    let _video = ''
    let shown = false;
    export function show() {
      shown = true;
    }
    export function hide() {
      shown = false;
    }
    
  
  
  
  </script>
  
  {#if shown}
  <div class="modal-wrapper">
    <div 
      class="" 
      style="position: absolute;
             left: 50%;
             top: 50%;
             width: calc(100vw - 4em);
             max-width: 32em;
             max-height: calc(100vh - 4em);
             overflow: auto;
             transform: translate(-50%,-50%);
             padding: 1em;
             border-radius: 0.2em;
             background: white;"
    >
    <button class="btn btn-light" on:click={() => hide()}>
      <span class="close" >&times;</span>
    </button>  
      <slot />
    </div>
  </div>
  
  {/if}
  
  
  
  <style>
      .modal-wrapper {
          background-color: rgb(0,0,0);
          background-color: rgba(0,0,0,0.4);
          position: fixed;
          /* position: absolute; */
          width: 100%;
          height: 100%;
          top: 0;
          left: 0;
      }
      .close {
          float: right;
          cursor: pointer;
      }
      .close:hover {
          font-weight: bold;
      }
  </style>