<script>
  import { onMount } from 'svelte';
  import { mangaApi } from '$lib/api/manga';
  import { mangas, currentPage, totalPages, loading } from '$lib/stores/manga';
  import MangaCard from '$lib/components/MangaCard.svelte';
  import Pagination from '$lib/components/Pagination.svelte';
  
  let searchTerm = '';
  
  async function loadMangas(page = 1) {
    $loading = true;
    try {
      const data = await mangaApi.getMangas(page);
      $mangas = data.items;
      $totalPages = data.pages;
      $currentPage = page;
    } catch (error) {
      console.error('Failed to load mangas:', error);
    } finally {
      $loading = false;
    }
  }
  
  async function handleSearch() {
    if (searchTerm.trim()) {
      $loading = true;
      try {
        const data = await mangaApi.searchMangas(searchTerm);
        $mangas = data.items;
        $totalPages = data.pages;
        $currentPage = 1;
      } catch (error) {
        console.error('Failed to search mangas:', error);
      } finally {
        $loading = false;
      }
    } else {
      loadMangas(1);
    }
  }
  
  onMount(() => {
    loadMangas();
  });
</script>

<div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
  <div class="px-4 py-6 sm:px-0">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Manga Gallery</h1>
      
      <div class="flex gap-4">
        <input
          type="text"
          bind:value={searchTerm}
          placeholder="Search mangas..."
          class="px-4 py-2 border rounded-md"
          on:keyup={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          on:click={handleSearch}
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Search
        </button>
      </div>
    </div>
    
    {#if $loading}
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    {:else}
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {#each $mangas as manga}
          <MangaCard {manga} />
        {/each}
      </div>
      
      <Pagination
        currentPage={$currentPage}
        totalPages={$totalPages}
        onPageChange={loadMangas}
      />
    {/if}
  </div>
</div>