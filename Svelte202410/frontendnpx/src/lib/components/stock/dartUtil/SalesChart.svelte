<script>
    import { onMount } from 'svelte';
    import Chart from 'chart.js/auto';
    import { key } from '$lib/stores/stock';
    import { getQuarterBalanceSheet } from './DartUtil.js';
    export let revenueData = [];
    let chartCanvas;
    let chart; // 차트 인스턴스 저장
    export let symbol;
    // revenueData = [
    //     {time: '2022-05-16', value: 5113},
    //     {time: '2022-08-16', value: 6514},
    //     {time: '2022-11-14', value: 8730},
    //     {time: '2023-03-09', value: 9656},
    //     {time: '2023-05-15', value: 7209},
    //     {time: '2023-08-14', value: 8662},
    //     {time: '2023-11-14', value: 10340},
    // ]
    
    // 문자열을 숫자로 변환하는 함수
    const stringToNumber = (str) => {
        if (typeof str === 'string') {
            return parseInt(str.replace(/,/g, ''));
        }
        return Math.floor(str);
    };


    
    $: if (revenueData && chartCanvas) {
        if (chart) {
            chart.destroy();
        }
        console.log('revenueData:', revenueData);
        // 데이터 포맷팅 수정
        const formattedData = revenueData.map(item => ({
            date: item.time.slice(2, 4) + item.time.slice(5, 7) + item.time.slice(8, 10),
            value: stringToNumber(item.value)
        }));

        console.log('포맷팅된 데이터:', formattedData);  // 데이터 확인용

        const ctx = chartCanvas.getContext('2d');
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: formattedData.map(d => d.date),
                datasets: [{
                    label: '',
                    data: formattedData.map(d => d.value),
                    backgroundColor: '#2962FF',
                    borderColor: '#2962FF',
                    borderWidth: 1,
                    barPercentage: 0.9,        // 막대 너비 조절 (0~1)
                    categoryPercentage: 0.5,    // 카테고리 너비 조절 (0~1)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                        position: 'top',
                    },
                    title: {
                        display: false,
                        text: '분기별 매출액'
                    }
                },
                layout: {
                    padding: {
                        right: 50  // 오른쪽 패딩 추가
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString() + '억';
                            }
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });
    }

    onMount(() => {
        return () => {
            if (chart) {
                chart.destroy();
            }
        };
    });
</script>

<!-- 데이터가 없을 때 처리 -->
{#if !revenueData || revenueData.length === 0}
    <div>데이터가 없습니다.</div>
{:else}
    <div class="dart-container">
        <div class="button-container">
            <button on:click={() => {
                getQuarterBalanceSheet(symbol, true);
            }}>
                새로고침
            </button>
        </div>
        <div class="chart-container">
            <canvas bind:this={chartCanvas}></canvas>
        </div>
    </div>
{/if}



<style>
    .dart-container {
        display: flex;  /* 가로 배열 */
        gap: 0px;     /* 요소 간 간격 */
        align-items: center;  /* 세로 중앙 정렬 */
    }

    .chart-container {
        flex: 1;       /* 남은 공간 차지 */
        position: relative;
        height: 200px;
        /* width: 100%; */
        margin: 0px;
    }

    .button-container {
        display: flex;
        flex-direction: column;  /* 세로 배열 */
        align-items: flex-start;
        justify-content: flex-start;
        gap: 5px;              /* 버튼 간 간격 */
    }

    button {
        padding: 0px;
        font-size: 0.7rem;
        /* 추가 버튼 스타일링 */
    }
</style>