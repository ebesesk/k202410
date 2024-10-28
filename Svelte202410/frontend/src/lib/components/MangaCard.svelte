<script>
  export let manga;
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
  }
</script>

<div class="bg-white rounded-lg shadow-lg overflow-hidden">
  <div class="aspect-w-3 aspect-h-4">
    <div class="w-full h-48 bg-gray-200 flex items-center justify-center">
      <span class="text-gray-500">{manga.folder_name}</span>
    </div>
  </div>
  <div class="p-4">
    <h2 class="text-lg font-semibold text-gray-900 truncate">
      {manga.folder_name}
    </h2>
    {#if manga.tags}
      <p class="mt-1 text-sm text-gray-500">
        {manga.tags}
      </p>
    {/if}
    <div class="mt-2 text-sm text-gray-600">
      <div>Pages: {manga.page}</div>
      <div>Created: {formatDate(manga.create_date)}</div>
    </div>
  </div>
</div>
