<script>
  export let currentPage;
  export let totalPages;
  export let onPageChange;
  
  $: pages = Array.from({ length: totalPages }, (_, i) => i + 1);
</script>

<div class="flex justify-center mt-6 space-x-2">
  <button
    class="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
    disabled={currentPage === 1}
    on:click={() => onPageChange(currentPage - 1)}
  >
    Previous
  </button>
  
  {#each pages as page}
    <button
      class="px-3 py-1 rounded {currentPage === page ? 'bg-blue-500 text-white' : 'bg-gray-200'}"
      on:click={() => onPageChange(page)}
    >
      {page}
    </button>
  {/each}
  
  <button
    class="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
    disabled={currentPage === totalPages}
    on:click={() => onPageChange(currentPage + 1)}
  >
    Next
  </button>
</div>