<script>
  import { fade } from 'svelte/transition';
  export let show = false;
  export let image = '';
  export let onClose = () => {};
  
  function handleKeydown(event) {
    if (event.key === 'Escape') {
      onClose();
    }
  }

  function stopPropagation(event) {
    event.stopPropagation();
  }
</script>

<svelte:window on:keydown={handleKeydown}/>

{#if show}
  <div
    class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
    on:click={onClose}
    transition:fade
  >
    <div 
      class="relative max-w-7xl mx-auto px-4 h-full flex items-center justify-center"
      on:click={stopPropagation}
    >
      <button
        class="absolute top-4 right-4 text-white text-xl p-2 hover:bg-gray-800 rounded-full"
        on:click={onClose}
      >
        ✕
      </button>
      <img
        src={image}
        alt="Enlarged view"
        class="max-h-[90vh] max-w-[90vw] object-contain"
      />
    </div>
  </div>
{/if}