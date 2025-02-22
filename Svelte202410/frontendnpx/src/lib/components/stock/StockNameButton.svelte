<script>
    import { onMount } from 'svelte';
    import { calculateTaxGains } from '$lib/stock/trade';
    export let trade;  // 전체 trade 객체를 전달받도록 수정
    export let code;
    export let name;
    export let date;
    export let assetCategory;
    export let searchByCode;

    let showActions = false;
    let popupX = 0;
    let popupY = 0;
    let isAll = false;

    function toggleActions(event) {
        if (event) {
            // 절대 위치 대신 상대 위치 사용
            const rect = event.target.getBoundingClientRect();
            popupX = rect.left;
            popupY = rect.bottom + window.scrollY; // 스크롤 위치 고려
            
            // 화면 경계 체크
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight + window.scrollY;
            const popupWidth = 120;
            const popupHeight = 80;
            
            // 오른쪽 경계 체크
            if (popupX + popupWidth > windowWidth) {
                popupX = popupX - popupWidth;
            }
            
            // 아래쪽 경계 체크
            if (popupY + popupHeight > windowHeight) {
                popupY = rect.top + window.scrollY - popupHeight; // 요소 위로 표시
            }
            
            showActions = !showActions;
            event.stopPropagation();
        }
    }

    async function toggleDetails() {
        try {
            if (!trade.taxData) {
                const taxData = await calculateTaxGains(code, trade.date);
                trade = { ...trade, taxData };  // 새 객체 생성으로 반응성 트리거
            }
            trade.showDetails = !trade.showDetails;
        } catch (error) {
            console.error('세금 계산 실패:', error);
        }
    }

    function handleClickOutside(event) {
        const actionButtons = document.querySelector('.action-buttons');
        if (actionButtons && !actionButtons.contains(event.target) && 
            !event.target.closest('.stock-link')) {
            showActions = false;
        }
    }

    onMount(() => {
        document.addEventListener('click', handleClickOutside);
        document.addEventListener('touchstart', handleClickOutside);
        return () => {
            document.removeEventListener('click', handleClickOutside);
            document.removeEventListener('touchstart', handleClickOutside);
        };
    });
</script>

<!-- 템플릿 부분 -->
<div class="stock-name-container">
    <a href="#" 
       class="stock-link"
       on:click|preventDefault={toggleActions}>
        {#if assetCategory.includes('usd')}
            {code}
        {:else}
            {name}
        {/if}
    </a>

    {#if showActions}
        <div class="action-buttons" 
            style="position: absolute; left: {popupX}px; top: {popupY}px;"
            on:mouseleave={() => showActions = false}
            on:touchstart|stopPropagation>
        {#if !isAll}
            <button on:click|stopPropagation={() => {
                isAll = true; 
                searchByCode(code); 
                showActions = false;
            }}>종목정보</button>
        {:else}
            <button on:click|stopPropagation={() => {
                isAll = false; 
                searchByCode(''); 
                showActions = false;
            }}>모두보기</button>
        {/if}
            <button 
                class="stock-link"
                on:click|preventDefault|stopPropagation={() => {
                    toggleDetails(); 
                    showActions = false;
                }}>
                {#if assetCategory?.includes('usd')}
                    {code}
                {:else}
                    {name}
                {/if}
            </button>
        </div>
    {/if}
</div>
<style>
    .stock-actions {
        position: relative;
        display: inline-block;
    }

    .action-buttons {
        position: fixed;
        z-index: 1000;
        background: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 0.5rem 0;
        min-width: 120px;
    }

    .action-buttons button {
        display: block;
        width: 100%;
        padding: 0.5rem 1rem;
        border: none;
        background: none;
        text-align: left;
        cursor: pointer;
        font-size: 0.8rem;
    }

    .action-buttons button:hover {
        background: #f5f5f5;
    }
</style>