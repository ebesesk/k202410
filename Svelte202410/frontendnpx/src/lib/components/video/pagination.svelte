<!-- src/lib/components/Pagination.svelte -->
<script>
    export let totalPages = 1;
    export let currentPage = 1;

    function changePage(page) {
        if (page < 1 || page > totalPages) return;
        // 페이지 변경 이벤트 발생
        dispatch('pageChange', page);
    }
</script>

<div class="pagination">
    <button on:click={() => changePage(currentPage - 1)} disabled={currentPage === 1}>
        이전
    </button>
    {#each Array(totalPages) as _, index}
        <button 
            class:selected={index + 1 === currentPage} 
            on:click={() => changePage(index + 1)}
        >
            {index + 1}
        </button>
    {/each}
    <button on:click={() => changePage(currentPage + 1)} disabled={currentPage === totalPages}>
        다음
    </button>
</div>

<style>
    .pagination {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    button {
        margin: 0 5px;
        padding: 5px 10px;
    }
    button.selected {
        font-weight: bold;
        background-color: #3498db;
        color: white;
    }
</style>