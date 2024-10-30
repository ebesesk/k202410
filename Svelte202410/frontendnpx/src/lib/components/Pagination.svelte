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

			// end가 start보다 작은 경우 처리
			if (end < start) end = start;

			return { start, end };
	}

	let inputPage = '';

	function handleSubmit() {
			const page = parseInt(inputPage);
			if (!isNaN(page) && page >= 1 && page <= totalPages) {
					onPageChange(page);
					inputPage = '';  // 입력 필드 초기화
			} else {
					alert('유효한 페이지 번호를 입력해주세요');
			}
	}
</script>

<div class="pagination">
	<!-- 첫 페이지 버튼 -->
	<button 
			disabled={currentPage === 1}
			on:click={() => onPageChange(1)}
	>
			&lt;&lt;
	</button>

	<!-- 이전 페이지 버튼 -->
	<button 
			disabled={currentPage === 1}
			on:click={() => onPageChange(currentPage - 1)}
	>
			&lt;
	</button>

	<!-- 첫 페이지 표시 -->
	{#if getPageRange(currentPage, totalPages).start > 1}
			<button 
					class:active={currentPage === 1}
					on:click={() => onPageChange(1)}
			>
					1
			</button>
			{#if getPageRange(currentPage, totalPages).start > 2}
					<span>...</span>
			{/if}
	{/if}

	<!-- 페이지 번호들 -->
	{#each Array.from({length: Math.max(0, getPageRange(currentPage, totalPages).end - getPageRange(currentPage, totalPages).start + 1)}) as _, i}
			{@const pageNum = getPageRange(currentPage, totalPages).start + i}
			<button 
					class:active={currentPage === pageNum}
					on:click={() => onPageChange(pageNum)}
			>
					{pageNum}
			</button>
	{/each}

	<!-- 마지막 페이지 표시 -->
	{#if getPageRange(currentPage, totalPages).end < totalPages}
			{#if getPageRange(currentPage, totalPages).end < totalPages - 1}
					<span>...</span>
			{/if}
			<button 
					class:active={currentPage === totalPages}
					on:click={() => onPageChange(totalPages)}
			>
					{totalPages}
			</button>
	{/if}

	<!-- 다음 페이지 버튼 -->
	<button 
			disabled={currentPage === totalPages}
			on:click={() => onPageChange(currentPage + 1)}
	>
			&gt;
	</button>

	<!-- 마지막 페이지 버튼 -->
	<button 
			disabled={currentPage === totalPages}
			on:click={() => onPageChange(totalPages)}
	>
			&gt;&gt;
	</button>
	<div class="page-input">
		<input 
				type="number" 
				bind:value={inputPage}
				min="1"
				max={totalPages}
				placeholder="페이지"
		>
		<button on:click={handleSubmit}>이동</button>
	</div>
</div>

<style>
	.pagination {
			display: flex;
			justify-content: center;
			gap: 0.5rem;
			margin: 1rem 0;
	}

	button {
			padding: 0.5rem 1rem;
			border: 1px solid #ddd;
			background: white;
			cursor: pointer;
			border-radius: 4px;
	}

	button:hover:not(:disabled) {
			background: #f0f0f0;
	}

	button:disabled {
			cursor: not-allowed;
			opacity: 0.5;
	}

	button.active {
			background: #007bff;
			color: white;
			border-color: #0056b3;
	}

	span {
			padding: 0.5rem;
	}

	.page-input {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        margin-left: 1rem;
    }

    .page-input input {
        width: 60px;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
    }

    .page-input button {
        padding: 0.5rem 1rem;
    }
</style>