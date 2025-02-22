<script>
    import { key } from "$lib/stores/stock";
    import { onMount } from 'svelte';
    import fastapi from '$lib/api';
    import { investmentStore } from '$lib/components/stock/investment/js/investmentStores.js';
    // onMount(async () => {
    //     const response = await fetch('/api/dart/list');
    //     const data = await response.json();
    // });
    function test() {
        const url = '/stock/dart'
        const params = {
            key: $key,
        }
        fastapi('get', url, params, (json) => {
            console.log(json);
        });
    }
    export function getQuarterBalanceSheet(symbol) {
        const url = '/stock/dart/balance-sheet'
        const params = {
            key: $key,
            symbol: symbol,
        }
        fastapi('get', url, params, (json) => {
            console.log('json:', json);
            // 스토어 업데이트
            // $investInfoMap[symbol].quarter = json.quarter;
            
            // console.log('저장된 데이터:', $investmentStore);

            let _quarter = [];
            for (let item of Object.values(json.quarter)) {
                if (item[0] && item[0].toString().startsWith('20')) {
                    let dateStr = item[0].toString();
                    let year = dateStr.slice(0, 4);
                    let month = dateStr.slice(4, 6);
                    let day = dateStr.slice(6, 8);
                    
                    // 기본 날짜 형식
                    let formattedDate = `${year}-${month}-${day}`;
                    
                    // 날짜 중복 확인 및 처리
                    while (_quarter.some(q => q.time === formattedDate)) {
                        let date = new Date(year, month - 1, day);
                        date.setDate(date.getDate() + 7);
                        
                        year = date.getFullYear();
                        month = String(date.getMonth() + 1).padStart(2, '0');
                        day = String(date.getDate()).padStart(2, '0');
                        formattedDate = `${year}-${month}-${day}`;
                    }

                    let value = stringToNumber(item[10].toString())/100000000;
                    _quarter.push({
                        time: formattedDate,
                        value: value, 
                        color: 'rgba(128, 128, 128, 0.5)'
                    });
                }
            }

            // 시간순으로 정렬
            _quarter.sort((a, b) => {
                const timeA = new Date(a.time).getTime();
                const timeB = new Date(b.time).getTime();
                return timeA - timeB;
            });

            quarterBalance[symbol] = _quarter;

            // quarterBalance[symbol] = _quarter;
            console.log('quarterBalance:', quarterBalance);
            if (!toggleQuarterChart.includes(symbol)) {
                toggleQuarterChart.push(symbol);
            } else {
                toggleQuarterChart = toggleQuarterChart.filter(s => s !== symbol);
            }
        });
    }

    function getBalanceSheet(symbol) {
        const url = '/stock/dart/balance-sheet'
        const params = {
            key: $key,
            symbol: symbol,
        }
        fastapi('get', url, params, (json) => {
            console.log('json:', json);
            // 스토어 업데이트
            $investmentStore = {
                ...$investmentStore,  // 기존 데이터 유지
                quarterBalanceSheet: {
                    ...$investmentStore.quarterBalanceSheet,
                    [symbol]: json.report_quarter
                }
            }
            
            // // 또는 setBalanceSheet 메서드 사용시
            // $investmentStore.setQuarterBalanceSheet(report_quarter);
            
            console.log('저장된 데이터:', $investmentStore);
        });
    }
</script>
<div class="dart-container">
    {#if showSalesChart}
        <SalesChart {revenueData} />
    {/if}
    <button on:click={toggleSalesChart}>
        매출액 차트 {showSalesChart ? '숨기기' : '보기'}
    </button>
</div>


<style>
    .dart-container {
        position: relative;
        width: 100%;
    }
</style>
