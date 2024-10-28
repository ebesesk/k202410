<script>
  import "../app.css";
  import { isAuthenticated } from "$lib/stores/auth";
  
  let showMobileMenu = false;
</script>

<div class="min-h-screen bg-gray-100">
  <nav class="bg-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <a href="/" class="text-2xl font-bold text-gray-800">Manga Gallery</a>
          </div>
          
          <div class="hidden md:ml-6 md:flex md:space-x-8">
            <a href="/" class="inline-flex items-center px-1 pt-1 text-gray-900">Home</a>
            <a href="/gallery" class="inline-flex items-center px-1 pt-1 text-gray-900">Gallery</a>
          </div>
        </div>
        
        <div class="hidden md:flex md:items-center md:ml-6">
          {#if $isAuthenticated}
            <button
              on:click={() => ($isAuthenticated = false)}
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
            >
              Logout
            </button>
          {:else}
            <a
              href="/login"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Login
            </a>
          {/if}
        </div>
        
        <button
          on:click={() => (showMobileMenu = !showMobileMenu)}
          class="md:hidden"
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>
    
    {#if showMobileMenu}
      <div class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1">
          <a href="/" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">Home</a>
          <a href="/gallery" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">Gallery</a>
        </div>
      </div>
    {/if}
  </nav>

  <main>
    <slot />
  </main>
</div>
