<script>
    import { onMount } from 'svelte';
    import { fastapi } from '$lib/realEstateApi';
    
    let aptList = [];
    let sidoList = [];
    let sigunguList = [];
    let dongList = [];
    let transactions = [];  // 추가: transactions 초기화
    
    let selectedSido = '';
    let selectedSigungu = '';
    let selectedDong = '';
    let selectedApt = '';

    // 페이지네이션 관련 변수들
    let currentPage = 1;
    let pageSize = 20;
    let totalPages = 0;
    let hasNext = false;
    let hasPrev = false;

    let sortColumn = 'dealYear';
    let sortType = 'desc';

    let selectedPyung = '';

    const sortColumns = {
        'aptNm': '아파트',
        'umdNm': '동',
        'excluUseAr': '면적(㎡)',
        'pyung': '평수',  // 정렬 불필요한 컬럼
        'floor': '층수',
        'dealAmount': '거래금액',
        'dealYear': '거래일자'
    };
    const pyungTypes = [
        { value: '', label: '전체 평수' },
        { value: 'under10', label: '10평 미만' },
        { value: 'py10', label: '10평대' },
        { value: 'py20', label: '20평대' },
        { value: 'py30', label: '30평대' },
        { value: 'over40', label: '40평 이상' }
    ];

    onMount(async () => {
        fetchSidoList();
    });

    function fetchSidoList() {
        fastapi('get', '/bdongcode/sido', {}, (json) => {
            sidoList = json.message;
            console.log('sidoList', sidoList);
        });
    }

    function fetchSigunguList() {
        console.log('sidoCode', selectedSido);
        selectedSigungu = '';
        selectedDong = '';
        selectedApt = '';
        let params = {sido_code: selectedSido}
        fastapi('get', `/bdongcode/sigungu`, params, (json) => {
            sigunguList = json.message;
            console.log('sigunguList', sigunguList);
        });
    }

    
    // fetchDongAptList 함수 수정
    function fetchDongAptList() {
        if (!selectedSigungu) {
            return;
        }

        let params = {
            sigungu_code: selectedSigungu,
            page: currentPage,
            page_size: pageSize,
            sort_column: sortColumn,
            sort_type: sortType
        }
        
        if (selectedDong) {
            params.dong_name = selectedDong;
        }
        if (selectedApt) {
            params.apt_name = selectedApt;
        }
        if (selectedPyung) {
            params.pyung_type = selectedPyung;
        }
        fastapi('get', `/transactionsprice/transactions`, params, (json) => {
            dongList = json.dong_list;
            aptList = json.apt_list;
            transactions = json.data;
            
            // 페이지네이션 정보 업데이트
            totalPages = json.pagination.total_pages;
            currentPage = json.pagination.current_page;
            hasNext = json.pagination.has_next;
            hasPrev = json.pagination.has_prev;
            
            console.log('페이지 정보:', {
                currentPage,
                totalPages,
                hasNext,
                hasPrev
            });
        });
    }


    function nextPage() {
        if (hasNext) {
            currentPage += 1;
            fetchDongAptList();
        }
    }

    function prevPage() {
        if (hasPrev) {
            currentPage -= 1;
            fetchDongAptList();
        }
    }

    function selectSigungu() {
        selectedDong = '';
        selectedApt = '';
        fetchDongAptList();
    }
    function selectDong() {
        selectedApt = '';
        fetchDongAptList();
    }
    function handleSort(column) {
        if (sortColumn === column) {
            // 같은 컬럼을 다시 클릭하면 정렬 방향을 변경
            sortType = sortType === 'asc' ? 'desc' : 'asc';
        } else {
            // 다른 컬럼을 클릭하면 해당 컬럼으로 내림차순 정렬
            sortColumn = column;
            sortType = 'desc';
        }
        fetchDongAptList();
    }

    // 페이지 범위 계산 함수
    function getPageRange() {
        const range = 5; // 표시할 페이지 번호 개수
        const start = Math.max(1, currentPage - Math.floor(range / 2));
        const end = Math.min(totalPages, start + range - 1);
        return Array.from({length: end - start + 1}, (_, i) => start + i);
    }

    function goToPage(page) {
        if (page >= 1 && page <= totalPages) {
            currentPage = page;
            fetchDongAptList();
        }
    }
    function getPyungType(pyung) {
        const pyungValue = Number(pyung);
        if (pyungValue < 10) return 'under10';
        if (pyungValue < 20) return 'py10';
        if (pyungValue < 30) return 'py20';
        if (pyungValue < 40) return 'py30';
        return 'over40';
    }

    function getPyungLabel(pyungType) {
        const labels = {
            'under10': '10평 미만',
            'py10': '10평대',
            'py20': '20평대',
            'py30': '30평대',
            'over40': '40평 이상'
        };
        return labels[pyungType] || '전체 평수';
    }

    function handlePyungClick(pyung) {
        const pyungType = getPyungType(pyung);
        selectedPyung = pyungType;
        currentPage = 1; // 페이지를 1로 리셋
        fetchDongAptList();
    }

    function clearPyungFilter() {
        selectedPyung = '';
        currentPage = 1;
        fetchDongAptList();
    }
</script>

<div class="container">
    <div class="select-container">
        <select bind:value={selectedSido} on:change={fetchSigunguList}>
            <option value="">시/도 선택</option>
            {#each sidoList as sido}
                <option value={sido.code}>{sido.name}</option>
            {/each}
        </select>
        <select bind:value={selectedSigungu} disabled={!selectedSido} on:change={selectSigungu}>
            <option value="">시/군/구 선택</option>
            {#each sigunguList as sigungu}
                <option value={sigungu.code}>{sigungu.name}</option>
            {/each}
        </select>
        <select bind:value={selectedDong} disabled={!selectedSigungu} on:change={selectDong}>
            <option value="">읍면동 선택</option>
            {#each dongList as dong}
                <option value={dong}>{dong}</option>
            {/each}
        </select>
        <select bind:value={selectedApt} disabled={!selectedSigungu} on:change={fetchDongAptList}>
            <option value="">아파트</option>
            {#each aptList as apt}
                <option value={apt}>{apt}</option>
            {/each}
        </select>
        <select bind:value={selectedPyung} disabled={!selectedSigungu} on:change={fetchDongAptList}>
            {#each pyungTypes as type}
                <option value={type.value}>{type.label}</option>
            {/each}
        </select>
    </div>
</div>

<!-- 페이지네이션 UI 수정 -->
{#if transactions.length > 0}
    <div class="pagination">
        <button on:click={() => goToPage(1)} disabled={currentPage === 1}>
            ≪
        </button>
        <button on:click={prevPage} disabled={!hasPrev}>
            ＜
        </button>
        
        {#each getPageRange() as page}
            <button 
                class:active={page === currentPage}
                on:click={() => goToPage(page)}
            >
                {page}
            </button>
        {/each}
        
        <button on:click={nextPage} disabled={!hasNext}>
            ＞
        </button>
        <button on:click={() => goToPage(totalPages)} disabled={currentPage === totalPages}>
            ≫
        </button>

        <span class="page-info">
            {currentPage} / {totalPages} 페이지
        </span>
    </div>
{/if}

    <!-- 거래 데이터 표시 -->
    <div class="transactions-container">
        <div class="filter-info">
            {#if selectedPyung}
                <span>필터: {getPyungLabel(selectedPyung)}</span>
                <button class="clear-filter" on:click={clearPyungFilter}>✕</button>
            {/if}
        </div>
        <table>
            <thead>
                <tr>
                    {#each Object.entries(sortColumns) as [column, label]}
                        <th 
                            class:no-sort={column === 'pyung'}
                            on:click={() => column !== 'pyung' && handleSort(column)}
                            class:active={sortColumn === column}
                            class:asc={sortColumn === column && sortType === 'asc'}
                            class:desc={sortColumn === column && sortType === 'desc'}
                        >
                            {label}
                            {#if sortColumn === column && column !== 'pyung'}
                                <span class="sort-arrow">
                                    {sortType === 'asc' ? '↑' : '↓'}
                                </span>
                            {/if}
                        </th>
                    {/each}
                </tr>
            </thead>
            <tbody>
                {#each transactions as transaction}
                    {@const area = parseFloat(transaction.excluUseAr) || 0}
                    {@const pyung = (area / 3.3058).toFixed(1)}
                    <tr>
                        <td>{transaction.aptNm}</td>
                        <td>{transaction.umdNm}</td>
                        <td>{area.toFixed(2)}</td>
                        <td 
                            class="pyung-cell" 
                            on:click={() => handlePyungClick(pyung)}
                            class:filtered={selectedPyung === getPyungType(pyung)}
                        >
                            {pyung}평
                        </td>
                        <td>{transaction.floor}</td>
                        <td>{transaction.dealAmount}만원</td>
                        <td>{transaction.dealYear}.{transaction.dealMonth}.{transaction.dealDay}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>




<style>
    .container {
        padding: 20px;
    }
    
    .select-container {
        margin-bottom: 15px;
    }
    
    select {
        width: 200px;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }
    
    select:focus {
        outline: none;
        border-color: #007bff;
    }

    .page-info {
        margin-left: 15px;
        color: #666;
        font-size: 14px;
        padding: 8px 12px;
        background-color: #f8f9fa;
        border-radius: 4px;
        border: 1px solid #ddd;
    }
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        margin: 20px 0;
        flex-wrap: wrap;
    }

    .pagination button {
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #fff;
        cursor: pointer;
        min-width: 40px;
        font-size: 14px;
        transition: all 0.2s ease-in-out;  /* 부드러운 전환 효과 */
    }

    .pagination button:hover:not(:disabled) {
        background-color: #e9ecef;
        border-color: #dee2e6;
        color: #007bff;
    }
    .pagination button:disabled {
        background-color: #f5f5f5;
        cursor: not-allowed;
        color: #999;
    }
    /* 현재 페이지 버튼 스타일 강화 */
    .pagination button.active {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);  /* 그림자 효과 */
    }

    .pagination button.active:hover {
        background-color: #0056b3;
        border-color: #0056b3;
    }

    .page-info {
        margin-left: 15px;
        color: #666;
        font-size: 14px;
        padding: 8px 12px;
        background-color: #f8f9fa;
        border-radius: 4px;
        border: 1px solid #ddd;
    }

    /* 첫 페이지, 마지막 페이지 버튼 스타일 */
    .pagination button:first-child,
    .pagination button:last-child {
        background-color: #f8f9fa;
    }

    /* 이전, 다음 버튼 스타일 */
    .pagination button:nth-child(2),
    .pagination button:nth-last-child(3) {
        background-color: #f8f9fa;
    }

    .transactions-container {
        margin-top: 20px;
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }

    th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* 테이블 행 호버 효과 */
    tbody tr {
        transition: background-color 0.2s ease-in-out;  /* 부드러운 전환 효과 */
    }

    tbody tr:hover {
        background-color: #f5f8ff;  /* 연한 파란색 배경 */
        cursor: pointer;  /* 마우스 커서 변경 */
    }

    /* 짝수/홀수 행 구분을 위한 스타일 (선택사항) */
    tbody tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    tbody tr:nth-child(even):hover {
        background-color: #f5f8ff;
    }

    /* 테이블 헤더 스타일 강화 */
    thead tr {
        background-color: #f5f5f5;
        border-bottom: 2px solid #ddd;
    }

    
    /* 각 컬럼별 너비 설정 */
    th:nth-child(1), td:nth-child(1) { width: 25%; } /* 아파트명 */
    th:nth-child(2), td:nth-child(2) { width: 15%; } /* 동 */
    th:nth-child(3), td:nth-child(3) { width: 10%; } /* 면적 */
    th:nth-child(4), td:nth-child(4) { width: 10%; } /* 층수 */
    th:nth-child(5), td:nth-child(5) { width: 15%; } /* 거래금액 */
    th:nth-child(6), td:nth-child(6) { width: 25%; } /* 거래일자 */

    th {
        background-color: #f5f5f5;
        cursor: pointer;
        user-select: none;
        position: relative;
        padding-right: 20px;  /* 화살표를 위한 공간 */
    }

    /* 텍스트 정렬 */
    td:nth-child(3), 
    td:nth-child(4), 
    td:nth-child(5) { 
        text-align: right; /* 숫자 데이터는 우측 정렬 */
    }

    th:hover {
        background-color: #e5e5e5;
    }

    th.active {
        background-color: #e0e0e0;
    }

    .sort-arrow {
        position: absolute;
        right: 5px;
        top: 50%;
        transform: translateY(-50%);
    }

    .transactions-container {
        margin-top: 20px;
        overflow-x: auto;  /* 테이블이 너무 클 경우 가로 스크롤 */
        width: 100%;
    }

    /* 정렬 방향에 따른 스타일 */
    th.asc .sort-arrow {
        color: #007bff;
    }

    th.desc .sort-arrow {
        color: #007bff;
    }

    /* 각 컬럼별 너비 설정 수정 */
    th:nth-child(1), td:nth-child(1) { width: 25%; } /* 아파트명 */
    th:nth-child(2), td:nth-child(2) { width: 15%; } /* 동 */
    th:nth-child(3), td:nth-child(3) { width: 10%; } /* 면적 */
    th:nth-child(4), td:nth-child(4) { width: 10%; } /* 평수 */
    th:nth-child(5), td:nth-child(5) { width: 10%; } /* 층수 */
    th:nth-child(6), td:nth-child(6) { width: 15%; } /* 거래금액 */
    th:nth-child(7), td:nth-child(7) { width: 15%; } /* 거래일자 */

    /* 숫자 데이터 우측 정렬 수정 */
    td:nth-child(3), 
    td:nth-child(4), 
    td:nth-child(5),
    td:nth-child(6) { 
        text-align: right;
    }

     /* 숫자 데이터 우측 정렬 - th와 td 모두 적용 */
    th:nth-child(3), td:nth-child(3),  /* 면적 */
    th:nth-child(4), td:nth-child(4),  /* 평수 */
    th:nth-child(5), td:nth-child(5),  /* 층수 */
    th:nth-child(6), td:nth-child(6) { /* 거래금액 */
        text-align: right;
    }

    /* 정렬 화살표가 있는 th의 경우 패딩 조정 */
    th:nth-child(3),
    th:nth-child(5),
    th:nth-child(6) {
        padding-right: 25px;  /* 화살표를 위한 여유 공간 */
    }

    /* 정렬 불가능한 th(평수)는 기본 패딩 유지 */
    th.no-sort {
        padding-right: 12px;
    }

    th.no-sort:hover {
        background-color: #f5f5f5;
    }
    .pyung-cell {
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .pyung-cell:hover {
        background-color: #e3f2fd;
    }

    .pyung-cell.filtered {
        background-color: #e3f2fd;
        font-weight: bold;
    }
    .filter-info {
        margin-bottom: 10px;
        padding: 8px;
        background-color: #f8f9fa;
        border-radius: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .clear-filter {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        padding: 0 5px;
        font-size: 16px;
    }

    .clear-filter:hover {
        color: #dc3545;
    }
    .select-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }

    .select-container select {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        min-width: 120px;
    }

    .select-container select:disabled {
        background-color: #f5f5f5;
        cursor: not-allowed;
    }
</style>