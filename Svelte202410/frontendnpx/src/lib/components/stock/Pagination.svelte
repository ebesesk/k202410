<!-- src/lib/components/Pagination.svelte -->
<script>
    // import { fetchTrades } from '$lib/stores/tradeStore';
    export let currentPage = 1;
    export let totalPages = 1;
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    // export let onPageChange = (page) => {};
    
    async function handlePageChange(page) {
        currentPage = page;
        dispatch('pageChange', page);  // 이벤트만 발생시키고 부모 컴포넌트에서 처리
    }
    let pages = [];
    
    $: {
        pages = [];
        let start = Math.max(1, currentPage - 2);
        let end = Math.min(totalPages, currentPage + 2);
        
        if (start > 1) {
            pages.push(1);
            if (start > 2) pages.push('...');
        }
        
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }
        
        if (end < totalPages) {
            if (end < totalPages - 1) pages.push('...');
            pages.push(totalPages);
        }
    }
</script>

<div class="pagination">
    <button 
        class="page-button"
        disabled={currentPage === 1}
        on:click={() => handlePageChange(currentPage - 1)}
    >
        &lt;
    </button>
    
    {#each pages as page}
        {#if page === '...'}
            <span class="ellipsis">...</span>
        {:else}
            <button 
                class="page-button"
                class:active={page === currentPage}
                on:click={() => handlePageChange(page)}
            >
                {page}
            </button>
        {/if}
    {/each}
    
    <button 
        class="page-button"
        disabled={currentPage === totalPages}
        on:click={() => handlePageChange(currentPage + 1)}
    >
        &gt;
    </button>
</div>

<style>
    .pagination {
        display: flex;
        gap: 2px;
        align-items: center;
        justify-content: center;
        margin: 0.5rem 0;
    }
    
    .page-button {
        padding: 2px 4px;
        min-width: 24px;
        height: 24px;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        border-radius: 3px;
        font-size: 11px;
        line-height: 1;
    }
    
    .page-button:disabled {
        cursor: not-allowed;
        opacity: 0.5;
    }
    
    .page-button.active {
        background: #2c3e50;
        color: white;
        border-color: #2c3e50;
    }
    
    .ellipsis {
        padding: 0 2px;
        font-size: 11px;
    }

    @media (max-width: 768px) {
        .page-button {
            min-width: 28px;
            height: 28px;
            font-size: 11px;
            padding: 2px 4px;
        }
    }
</style>