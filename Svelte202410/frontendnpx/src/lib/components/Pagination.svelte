<script>
    export let currentPage;
    export let totalPages;
    export let onPageChange;

    function getPageRange(currentPage, pages) {
        const range = 2;
        let start = Math.max(1, currentPage - range);
        let end = Math.min(pages, currentPage + range);

        if (start > 1) start = Math.max(2, start);
        if (end < pages) end = Math.min(pages - 1, end);

        return { start, end };
    }
</script>

<div class="pagination">
    <button 
        disabled={currentPage === 1}
        on:click={() => onPageChange(1)} 
        aria-label="첫 페이지"
    >
        《
    </button>
    <button 
        disabled={currentPage === 1}
        on:click={() => onPageChange(currentPage - 1)}
        aria-label="이전 페이지"
    >
        〈
    </button>

    {#if getPageRange(currentPage, totalPages).start > 2}
        <button on:click={() => onPageChange(1)}>1</button>
        <span class="ellipsis">...</span>
    {/if}

    {#each Array(getPageRange(currentPage, totalPages).end - getPageRange(currentPage, totalPages).start + 1) as _, i}
        {@const pageNum = getPageRange(currentPage, totalPages).start + i}
        <button 
            class:active={currentPage === pageNum}
            on:click={() => onPageChange(pageNum)}
        >
            {pageNum}
        </button>
    {/each}

    {#if getPageRange(currentPage, totalPages).end < totalPages - 1}
        <span class="ellipsis">...</span>
        <button on:click={() => onPageChange(totalPages)}>{totalPages}</button>
    {/if}

    <button 
        disabled={currentPage === totalPages}
        on:click={() => onPageChange(currentPage + 1)}
        aria-label="다음 페이지"
    >
        〉
    </button>
    <button 
        disabled={currentPage === totalPages}
        on:click={() => onPageChange(totalPages)}
        aria-label="마지막 페이지"
    >
        》
    </button>
</div>

<style>
    .pagination {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 20px;
    }

    .ellipsis {
        padding: 5px 10px;
        color: #666;
    }

    .pagination button {
        min-width: 35px;
        height: 35px;
        padding: 0 5px;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .pagination button:disabled {
        background: #f5f5f5;
        cursor: not-allowed;
    }

    .pagination button.active {
        background: #007bff;
        color: white;
        border-color: #007bff;
    }
</style>