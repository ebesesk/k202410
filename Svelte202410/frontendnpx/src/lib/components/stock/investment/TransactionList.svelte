<!-- src/lib/components/stock/investment/TransactionList.svelte -->
<!-- src/lib/components/stock/investment/TransactionList.svelte -->
<script>
    // import { investmentStore } from '$lib/stores/stock';
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    import { loadTransactions, investmentStore } from './js/investmentStores';
    import { onMount } from 'svelte';
    
    onMount(async () => {
        await loadTransactions();
    });

    $: transactions = $investmentStore.transactions;
    const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('http://', 'https://') || 'https://api2410.ebesesk.synology.me';

    function handlePageChange(newPage) {
        console.log('newPage:', newPage);
        console.log('transactions:', transactions);
        console.log('$investmentStore.pagination:', $investmentStore.pagination);
        console.log('$investmentStore.transactions:', $investmentStore.transactions);
        dispatch('pageChange', newPage);
    }
    // 날짜 포맷팅 함수
    function formatDate(dateString) {
        const date = new Date(dateString);
        const dateStr = date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).replace(/\. /g, '-').replace('.', '');  // 2024-02-15 형식으로 변환;
        const timeStr = date.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        return { date: dateStr, time: timeStr };
    }
</script>

<div class="transaction-list">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
            <tr>
                <th>날짜</th>
                <th>유형</th>
                <th>자산</th>
                <th class="number">수량</th>
                <th class="number">가격</th>
                <th class="number">금액</th>
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            {#each $investmentStore.transactions as transaction}
                <tr>
                    <td class="date-cell">
                        <span class="date">{formatDate(transaction.date).date}</span>
                        <!-- <span class="time">{formatDate(transaction.date).time}</span> -->
                    </td>
                    <td>{transaction.type}</td>
                    <td>{transaction.asset?.name || '-'}</td>
                    <td class="number">{transaction.quantity?.toLocaleString() || '-'}</td>
                    <td class="number">{transaction.price?.toLocaleString() || '-'}</td>
                    <td class="number">{transaction.amount?.toLocaleString()}</td>
                </tr>
            {/each}
        </tbody>
    </table>

    <div class="pagination">
        <button 
            disabled={$investmentStore.pagination.transactions.currentPage === 1}
            on:click={() => handlePageChange($investmentStore.pagination.transactions.currentPage - 1)}
        >
            이전
        </button>
        <span>
            {$investmentStore.pagination.transactions.currentPage} / {$investmentStore.pagination.transactions.totalPages}
        </span>
        <button 
            disabled={$investmentStore.pagination.transactions.currentPage === $investmentStore.pagination.transactions.totalPages}
            on:click={() => handlePageChange($investmentStore.pagination.currentPage + 1)}
        >
            다음
        </button>
    </div>
</div>

<style>
    table {
        font-size: 0.7rem;  /* 12px로 더 작게 */
    }
    
    th, td {
        padding: 0.15rem 0.3rem;
    }
    
    th {
        text-align: left;
        font-weight: 500;
        text-transform: uppercase;
        color: #6b7280;
    }
    
    td {
        white-space: nowrap;
    }
    
    .number {
        text-align: right;
    }

    .date-cell {
        line-height: 1;
    }

    .date {
        display: block;
    }

    .time {
        display: block;
        color: #6b7280;  /* 시간은 회색으로 */
    }
    .pagination button {
        padding: 0.1rem 0.2rem; /* 버튼 크기 줄이기 */
        font-size: 0.7rem; /* 글꼴 크기 줄이기 */
        border-radius: 3px; /* 모서리 둥글기 */
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        transition: background 0.2s;
    }

    .pagination button:hover {
        background: #f5f5f5;
    }

    .pagination button:disabled {
        background: #e0e0e0;
        cursor: not-allowed;
    }
</style>