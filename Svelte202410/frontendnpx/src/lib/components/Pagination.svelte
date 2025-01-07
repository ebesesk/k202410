<script>
    import { createEventDispatcher } from 'svelte';
    import { currentPage } from '$lib/stores/galleryStore';
    
    export let totalPages //= 1;
    
    const dispatch = createEventDispatcher();
    
    function changePage(page) {
        if (page >= 1 && page <= totalPages) {
            dispatch('pageChange', page);
        }
    }

    $: pages = Array.from({ length: totalPages }, (_, i) => i + 1);
    $: visiblePages = pages.filter(page => 
        page === 1 || 
        page === totalPages || 
        (page >= $currentPage - 2 && page <= $currentPage + 2)
    ).reduce((acc, page, i, arr) => {
        if (i > 0 && page - arr[i-1] > 1) {
            acc.push('...');
        }
        acc.push(page);
        return acc;
    }, []);
</script>

<div class="pagination">
    <button 
        class="page-button" 
        disabled={$currentPage === 1}
        on:click={() => changePage($currentPage - 1)}
    >
        이전
    </button>
    
    {#each visiblePages as page}
        {#if page === '...'}
            <span class="ellipsis">...</span>
        {:else}
            <button 
                class="page-button {page === $currentPage ? 'active' : ''}"
                on:click={() => changePage(page)}
            >
                {page}
            </button>
        {/if}
    {/each}
    
    <button 
        class="page-button" 
        disabled={$currentPage === totalPages}
        on:click={() => changePage($currentPage + 1)}
    >
        다음
    </button>
</div>

<style>
    .pagination {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .page-button {
        padding: 0.5rem 1rem;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        border-radius: 4px;
    }

    .page-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .page-button.active {
        background: #4CAF50;
        color: white;
        border-color: #45a049;
    }

    .ellipsis {
        padding: 0.5rem;
    }
</style>