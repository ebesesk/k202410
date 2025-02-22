<script>
    import { createEventDispatcher } from 'svelte';
    
    export let totalPages = 1;
    export let currentPage = 0;  // 0부터 시작하도록 변경
    
    const dispatch = createEventDispatcher();
    
    function changePage(newPage) {
        if (newPage >= 0 && newPage < totalPages) {  // 범위 체크 수정
            dispatch('pageChange', newPage);
        }
    }

    $: pageNumbers = calculatePageNumbers(currentPage, totalPages);

    function calculatePageNumbers(current, total) {
        const pages = [];
        const maxVisible = 5;

        if (total <= maxVisible) {
            for (let i = 0; i < total; i++) {  // 0부터 시작
                pages.push(i);
            }
        } else {
            // 항상 첫 페이지(0) 표시
            pages.push(0);
            
            if (current > 2) {  // 조건 수정
                pages.push('...');
            }
            
            // 현재 페이지 주변 페이지 표시
            for (let i = Math.max(1, current - 1); i <= Math.min(total - 2, current + 1); i++) {
                pages.push(i);
            }
            
            if (current < total - 3) {  // 조건 수정
                pages.push('...');
            }
            
            // 항상 마지막 페이지 표시
            if (total > 1) {
                pages.push(total - 1);  // 마지막 페이지는 total - 1
            }
        }
        
        return pages;
    }
    
</script>

<nav class="pagination" aria-label="Pagination">
    <button 
        class="page-button"
        on:click={() => changePage(currentPage - 1)}
        disabled={currentPage === 0}  
        aria-label="Previous page"
    >
        이전
    </button>

    {#each pageNumbers as pageNum}
        {#if pageNum === '...'}
            <span class="ellipsis">...</span>
        {:else}
            <button 
                class="page-button {pageNum === currentPage ? 'active' : ''}"
                on:click={() => changePage(pageNum)}
                aria-current={pageNum === currentPage ? 'page' : undefined}
                aria-label="Page {pageNum + 1}" 
            >
                {pageNum + 1}  <!-- 표시되는 숫자는 1부터 시작하도록 -->
            </button>
        {/if}
    {/each}

    <button 
        class="page-button"
        on:click={() => changePage(currentPage + 1)}
        disabled={currentPage === totalPages - 1}  
        aria-label="Next page"
    >
        다음
    </button>
</nav>

<style>
    .pagination {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        justify-content: center;
        margin: 1rem 0;
    }

    .page-button {
        padding: 0 0 0 0;
        margin: 0;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        border-radius: 3px;
        min-width: 1.5rem;  /* 너비 축소 */
        height: 1.5rem;    /* 높이 추가 */
        font-size: 11px;   /* 글자 크기 축소 */
        text-align: center;
        line-height: 1.5rem;  /* 세로 중앙 정렬 */
        /* 폰트 굵기 */
        font-weight: 500;
        /* 문자 가운데 정렬 */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .page-button:hover:not(:disabled) {
        background: #f0f0f0;
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
        color: #666;
    }
</style>