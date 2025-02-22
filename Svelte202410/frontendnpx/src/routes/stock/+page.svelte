<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { browser } from '$app/environment';
    import {onDestroy} from 'svelte';    
    import { slide } from 'svelte/transition';  // slide 트랜지션 추가
    import fastapi from '$lib/api';
    import { username } from '$lib/store';
    import { 
        accno_list, 
        accno_codes, 
        key, 
        selectedStocks, 
        investInfoMap, 
        candleStore, 
        chartDataStore, 
        sortedCodes,
        trade_keyword,
        dartData
    } from "$lib/stores/stock";
    import { get } from 'svelte/store';
    import { access_token } from '$lib/store';
    import { createChart } from 'lightweight-charts';
    import { numberToKorean, formatNumber } from '$lib/util';
    import { calculateFeeTax } from '$lib/stock/FeeTax';
    import { calculateTaxGains } from '$lib/stock/trade';  
    

    // investment 페이지
    // import TransactionPeriodicReturn from '$lib/components/stock/investment/forms/TransactionPeriodicReturn.svelte';
    import { investmentStore, loadAssets, loadAccounts } from '$lib/components/stock/investment/js/investmentStores';
    import TransactionsList from '$lib/components/stock/investment/forms/TransactionsList.svelte';
    import InvestmentButton from '$lib/components/stock/investment/InvestmentButton.svelte';
    import AccountForm from '$lib/components/stock/investment/AccountForm.svelte';
    import AccountList from '$lib/components/stock/investment/AccountList.svelte';
    import AccountInitialize from '$lib/components/stock/investment/AccountInitialize.svelte';
    // import AccountEditForm from '$lib/components/stock/investment/AccountEditForm.svelte';
    import AssetList from '$lib/components/stock/investment/AssetList.svelte';
    import AssetForm from '$lib/components/stock/investment/AssetForm.svelte';
    import AssetInitialize from '$lib/components/stock/investment/AssetInitialize.svelte';
    import TransactionForm from '$lib/components/stock/investment/TransactionForm.svelte';
    import TransactionSummary from '$lib/components/stock/investment/TransactionSummary.svelte';
    import TransactionList from '$lib/components/stock/investment/TransactionList.svelte';
    
    // 환율 정보 입력
    import ExchangeRateForm from '$lib/components/stock/investment/forms/ExchangeRateForm.svelte';
    
    // 투자 수익 계산
    import TransactionReturn from '$lib/components/stock/investment/forms/TransactionReturn.svelte';
    // 월별/연도별 수익율 조회
    import TransactionPeriodicReturn from '$lib/components/stock/investment/forms/TransactionPeriodicReturn.svelte';

    // 매출 차트
    import SalesChart from '$lib/components/stock/dartUtil/SalesChart.svelte'; 
    import { getQuarterBalanceSheet } from '$lib/components/stock/dartUtil/DartUtil.js';

    // 재무제표 데이터 로드
    // import DartUtil from '$lib/components/stock/dartUtil/DartUtil.svelte';


    import KeyInputForm from '$lib/components/stock/KeyInputForm.svelte';
    import AccountTable from '$lib/components/stock/AccountTable.svelte';
    import TaxDetailRow from '$lib/components/stock/TaxDetailRow.svelte'; // 양도소득 상세 표시
    import StockNameButton from '$lib/components/stock/StockNameButton.svelte'; // 종목명 클릭시 버튼 컴퍼넌트 표시
    import Pagination from '$lib/components/stock/Pagination.svelte';
    import AssetSummary from '$lib/components/stock/AssetSummary.svelte';




    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
  
    onMount(async () => {
        if (browser && $key) {
            getInterestStocks();
            getTradeAlltags();
            // $chartDataStore = {};
        }
        // await Promise.all([
        //     loadAssets(),
        //     loadAccounts()
        // ]);
    });
    // chartData가 변경될 때마다 차트 업데이트
    $: if (chartData && candleSeriesMap) {
        updateChartData(chartData);
    }
    
    $: accno_list, accno_codes, key, selectedStocks, investInfoMap;
    
    let appkey = '';
    let appsecretkey = '';
    let cname = '';     
    let isSetupKey = false;
    let setupKeyLoading = false;
    function setupLsOpenApiDb() {
        if (!$key || !appkey || !appsecretkey) {
            isSetupKey = !isSetupKey;
            return;
        }
        // setupKeyLoading = true;
        let params = {
            // key: $key, 
            appkey: appkey, 
            appsecretkey: appsecretkey,
            cname: cname,
            username: $username
        }
        console.log('params:', params);
        fastapi('post', '/stock/setup_ls_open_api_db'+'?key='+$key, params, (json) => {
            console.log('json:', json);
            // setupKeyLoading = false;
            isSetupKey = !isSetupKey;
        });
    }


    let isLoading = false;
   
    // 계좌 정보 조회
    function fetchAccnoList() {
        if (!$key) {
            return;
        }

        isLoading = true;
        let params = {key: $key}
        
        fastapi('get', '/stock/accno', params, (json) => {
            // $accno_list = json.accno_list;
            accno_list.set(json.accno_list);
            console.log('json.accno_list:', json.accno_list);
            accno_codes.set(json.accno_list.slice(3).map(row => row[0]));
            console.log('accno_codes:', $accno_codes);
            isLoading = false;
        }, (error) => {
            console.error('Error:', error);
            isLoading = false;
        });
    }

    // 시작: 관심종목 불러오기 db정보 + 현재가 조회
    let shcodes = [];
    let accnoCodes = [];
    // let interestCodes = [];
    let _stocks = [];
    
    let multi_price = [];
    let loadingInterestStocks = false;
    function getInterestStocks() {      // 시작
        if (!$key) return;
        let params = {key: $key}
        loadingInterestStocks = true;
        fastapi('get', '/stock/get_interest_stocks', params, (json) => {

            shcodes = json.shcodes;
            _stocks = json._stocks;
            accnoCodes = json.accno_codes;
            multi_price = json.multi_price;
            accno_list.set(json.accno_list);
            // accno_list = accno_list.set(json.accno_list);
            console.log('_stocks:', _stocks)
            console.log('accnoCodes:', accnoCodes)
            console.log('shcodes:', shcodes)
            console.log('multi_price:', multi_price)
            console.log('accno_list:', $accno_list)
            // // 차트 업데이트
            // const chartData = {};
            // for (const stock of multi_price) {
            //     chartData.body = {
            //         shcode: stock.종목코드,
            //         open: Number(stock.시가),
            //         high: Number(stock.고가),
            //         low: Number(stock.저가),
            //         close: Number(stock.현재가),
            //         volume: Number(stock.거래량),
            //         chetime: stock.체결시간
            //     };
            //     updateRealtimeChart(chartData);
            // }


            // 현재 $investInfoMap의 모든 코드 가져오기
            const currentCodes = Object.keys($investInfoMap);
            // _stocks의 모든 종목코드 가져오기
            const newCodes = _stocks.map(stock => stock.종목코드);
            // _stocks에 없는 코드 삭제
            currentCodes.forEach(code => {
                if (!newCodes.includes(code)) {
                    delete $investInfoMap[code];
                }
            });

            for (let i = 0; i < json._stocks.length; i++) {
                const code = json._stocks[i].종목코드;
                if (!$investInfoMap[code]) {
                    $investInfoMap[code] = {};
                }
                $investInfoMap[code].db = {};
                $investInfoMap[code].db = json._stocks[i];
                // console.log('json._stocks[i]:', json._stocks[i], code);
                // $investInfoMap[code].db.한글기업명 = json._stocks[i].한글기업명;
                // $investInfoMap[code].db.업종구분명 = json._stocks[i].업종구분명;
                // $investInfoMap[code].db.시장구분 = json._stocks[i].시장구분;
            }

            $investInfoMap = {...$investInfoMap}; // 반응성 트리거
            addMultiPrice(json.multi_price);
            console.log('investInfoMap:', $investInfoMap);
            console.log('$selectedStocks:', $selectedStocks);
            loadingInterestStocks = false;  // 로딩 완료
        });
    }
    
    // key 초기화 함수 추가
    function clearKey() {
        key.set('');
        accno_list.set([]);
    }
    

    // //////////////////////////////////////////////////////////////////////////////////
    // 종목코드로 투자 정보 조회
    function searchInvestInfo(shcode) {
        if (!$key) return;

        let params = {key: $key, gicode: shcode}
        fastapi('get', '/stock/investinfo_t3320', params, (json) => {
            // console.log('json:', json);
            $investInfoMap[shcode].t3320OutBlock = json.investinfo.t3320OutBlock;
            $investInfoMap[shcode].t3320OutBlock1 = json.investinfo.t3320OutBlock1;
            $investInfoMap = {...$investInfoMap};  // 반응성 트리거
            console.log('investInfoMap:', $investInfoMap);
            // return json.investinfo;
        }, (error) => {
            console.error('Error:', error);
        });
    }

    // 종목코드로 투자 정보 조회 멀티
    let loadingMultiInvestInfo = false;
    function getMultiInvestInfo() {
        if (!$key) return;
        loadingMultiInvestInfo = true;
        let shcodes_str = shcodes.join(',');
        // shcodes_str = '033100'
        let params = {
            key: $key, 
            shcodes: shcodes_str
        }
        fastapi('get', '/stock/investinfo_t3320_list', params, (json) => {
            if (json.investinfo_list) {
                console.log('json:', json);
                const investinfo_list = json.investinfo_list;
                for (const investinfo of investinfo_list) {
                let code = investinfo.t3320OutBlock1.기업코드.slice(1, 7);
                console.log('investinfo:', code, investinfo);
                $investInfoMap[code].t3320OutBlock = investinfo.t3320OutBlock;      // 종목코드로 투자 정보 조회
                $investInfoMap[code].t3320OutBlock1 = investinfo.t3320OutBlock1;    // 종목코드로 투자 정보 조회
                $investInfoMap = {...$investInfoMap};  // 반응성 트리거
                // console.log('investInfoMap.t3320OutBlock1:', $investInfoMap);
                }
                console.log('investInfoMap:', $investInfoMap);
                loadingMultiInvestInfo = false;
            } else {
                console.log('investinfo_list:', json);
                loadingMultiInvestInfo = false;
            }
        }, (error) => {
            console.error('Error:', error);
            loadingMultiInvestInfo = false;
        });
    }

    // 멀티 현재가 조회
    function getMultiPrice() {
        if (!$key) return;
        let params = {
            key: $key,
            shcodes_str: shcodes.join('')
        }
        fastapi('get', '/stock/multi_t8407', params, (json) => {
            console.log('multiPrice:', multi_price);
            return json.multi_price_list;
        });
    }

    // 멀티현재가 $investInfoMap에 추가
    function addMultiPrice(multi_price) {

        for (const price of multi_price) {
            const code = price.종목코드;  // 종목코드
            // 해당 종목코드의 객체가 없으면 초기화
            if (!$investInfoMap[code]) {
                $investInfoMap[code] = {};
            }
            
            // t8407OutBlock1이 없으면 초기화
            if (!$investInfoMap[code]['t8407OutBlock1']) {
                $investInfoMap[code]['t8407OutBlock1'] = {};
            }
            
            // 현재가 데이터 업데이트
            for (const _key in price) {
                if (_key !== '종목코드') {
                    $investInfoMap[code]['t8407OutBlock1'][_key] = price[_key];
                }
            }
            // 캔들 데이터 업데이트
            $candleStore[code] = {
                open: Number(price.시가),
                high: Number(price.고가),
                low: Number(price.저가),
                close: Number(price.현재가)
            };
            
            // 반응성 트리거를 위한 재할당
            $candleStore = { ...$candleStore };
        }
        // 반응성 트리거를 위한 객체 복사
    }
    
    
    ///////////////////////////////////////////////////////////////////주식차트 조회 차트 그리기
    
    let chartElement;  // 차트 엘리먼트 참조
    let chartContainers = new Map(); // 각 종목별 차트 컨테이너 관리
    let charts = new Map();          // 각 종목별 차트 인스턴스 관리
    let candleSeriesMap = new Map();    // 각 종목별 캔들시리즈 관리
    let volumeSeriesMap = new Map();   // 각 종목별 거래량시리즈 관리
    let additionalSeriesMap = new Map();    // 각 종목별 추가 시리즈 관리
    let chartData = [];             // 차트 데이터 관리
    let chartStock = null;          // 현재 차트 종목 관리
    let showChart = false;          // 차트 표시 여부 관리
    let isLoadingChart = false;    // 차트 로딩 여부 관리
    let currentChartCode = null;
    
    // chartElement가 변경될 때마다 실행되는 반응형 구문
    $: if (chartElement && stock && showChart) {
        const code = stock.db.종목코드;
        chartContainers.set(code, chartElement);
        console.log('차트 컨테이너 설정:', code, chartElement);
        
        // 차트 초기화 및 데이터 표시
        initializeChart(code).then(() => {
            if ($chartDataStore[code]) {
                updateChartData($chartDataStore[code]);
            }
        });
    }
    
    // chartPeriod 변경 감지
    // $: if (chartPeriod && currentChartCode && showChart) {
    //     handleStockClick(currentChartCode);  // 현재 선택된 종목 다시 조회
    // }
    
    const bindChart = (node, code) => {
        console.log('bindChart 호출:', code, node);
        if (node && code === currentChartCode) {
            chartContainers.set(code, node);
            
            // DOM이 바인딩된 후 차트 초기화 및 데이터 표시
            setTimeout(async () => {
                await initializeChart(code);
                if ($chartDataStore[code]) {
                    updateChartData($chartDataStore[code]);
                    console.log('charts: ', charts);
                }
            }, 0);
        }
    };
    
    async function toggleChart() {
        $selectedStocks = {};
        $selectedStocks[stock.db.종목코드] = true;
        $selectedStocks = {...$selectedStocks};
        if (showChart) {
            showChart = false;
            view_selected_stocks = false;
        } else {
            showChart = true;
            view_selected_stocks = true;
            if (currentChartCode) {
                if (charts.has(currentChartCode)) {
                    charts.get(currentChartCode).remove();
                    charts.delete(currentChartCode);
                }
                candleSeriesMap.delete(currentChartCode);
                volumeSeriesMap.delete(currentChartCode);
                chartContainers.delete(currentChartCode);
                additionalSeriesMap.delete(currentChartCode);
                currentChartCode = null;
            }
        }
    }
    let qrycnt = 100; // 차트 데이터 개수
    let chartPeriod = "2"; // 차트 기간

    // DB에 차트 데이터 저장 조회
    async function getChartData(_code) {
        return new Promise((resolve, reject) => {
            try {
                let kwargs = {
                    "shcode": _code,
                    "gubun": chartPeriod, // 2:일봉, 3:주봉, 4:월봉 5:년봉
                    "qrycnt": qrycnt,
                    "sdate": "",
                    "edate": "",
                    "cts_date": " ",
                    "comp_yn": "N",
                    "sujung": "Y"
                }
                const params = {
                    key: $key,
                    path: '/stock/chart',
                    tr_cd: 't8410',
                    kwargs: kwargs
                };

                // console.log('getChartData params:', params);

                fastapi('post', '/stock/get_chart_t8410', params, (json) => {
                    if (json.result) {
                        console.log('json.result:', json.result);
                        $chartDataStore[_code] = {
                            data: json.result[_code].data,
                            chartPeriod: json.result[_code].chartPeriod
                        };
                        $chartDataStore = {...$chartDataStore};
                        console.log('차트 데이터 저장:', $chartDataStore[_code]);
                        resolve($chartDataStore[_code]);

                    } else {
                        reject(new Error('차트 데이터 없음'));
                    }
                });
            } catch (error) {
                reject(error);
            }
        });
    }
    // 로딩 상태 표시를 위한 스타일 추가
    $: chartContainerClass = `chart-container ${isLoadingChart ? 'loading' : ''}`;

    // 차트 데이터 조회 함수
    async function getChartT8410() {
        if (!$key) return;
        const code = stock.db.종목코드;
        try {
            chartStock = stock.db.종목코드;
            let path = '/stock/chart';
            let tr_cd = 't8410';
            console.log('stock:', stock.db.종목코드);
            console.log('qrycnt:', qrycnt);
            console.log('chartPeriod:', chartPeriod);
            // 날짜 계산
            const today = new Date();
            const sdate = new Date(today.setDate(today.getDate() - qrycnt))
                .toISOString().slice(0,10).replace(/-/g,'');
            const edate = new Date()
            .toISOString().slice(0,10).replace(/-/g,'');

            let kwargs = {
                "shcode": stock.db.종목코드,
                "gubun": chartPeriod, // 2:일봉, 3:주봉, 4:월봉 5:년봉
                "qrycnt": qrycnt,
                "sdate": sdate,
                "edate": edate,
                "cts_date": "",
                "comp_yn": "N",
                "sujung_yn": "Y"
            }

            // await initializeChart(stock.db.종목코드);
            let params = {key: $key, path: path, tr_cd: tr_cd, kwargs: kwargs}
            await sleep(1000);
            fastapi('post', '/stock/get_lsopenapi', params, (json) => {
                if (json.result?.t8410OutBlock1) {
                    $chartDataStore[code] = {
                        data: json.result.t8410OutBlock1,
                        chartPeriod: chartPeriod
                    };
                    $chartDataStore = {...$chartDataStore};  // 반응성 트리거
                }
            });
        } catch (error) {
            console.error('차트 데이터 조회 실패:', error);
        }
    }


    // 차트 초기화 함수
    async function initializeChart(code) {
        console.log('initializeChart 시작:', code);
        
        // 초기 검증
        if (!browser || !chartContainers.get(code)) {
            console.error('차트 초기화 실패: browser 또는 container 없음', { browser, container: chartContainers.get(code), code });
            return;
        }
        
        try {
            const container = chartContainers.get(code);
            
            // 기존 차트 정리
            if (charts.has(code)) {
                charts.get(code).remove();
                charts.delete(code);
                candleSeriesMap.delete(code);
                volumeSeriesMap.delete(code);
                additionalSeriesMap.delete(code);
            }

            // 차트 기본 옵션 설정
            const chartOptions = {
                width: container.clientWidth,
                height: container.clientHeight,
                layout: {
                    background: { color: '#ffffff' },
                    textColor: '#333',
                },
                grid: {
                    vertLines: { color: '#f0f0f0' },
                    horzLines: { color: '#f0f0f0' },
                },
                // 메인 차트 영역 (캔들스틱)
                rightPriceScale: {
                    scaleMargins: { top: 0.01, bottom: 0.3 },
                    autoScale: true,
                    mode: 1,  // 로그 스케일
                    borderVisible: false,
                    entireTextOnly: true,
                    drawTicks: false,
                },
                // 보조지표 영역 설정
                overlayPriceScales: {
                    // 거래량 차트 영역
                    volume: {
                        scaleMargins: { top: 0.7, bottom: 0.1 },
                        autoScale: true,
                    },
                    // 매출액 차트 영역
                    prediction: {
                        scaleMargins: { top: 0.7, bottom: 0.02 },
                        autoScale: true,
                        borderColor: '#2962FF',
                    },
                },
                // 스크롤/확대축소 비활성화
                handleScroll: {
                    mouseWheel: false,
                    pressedMouseMove: false,
                    horzTouchDrag: true,
                    vertTouchDrag: true,
                },
                handleScale: {
                    axisPressedMouseMove: false,
                    mouseWheel: false,
                    pressedMouseMove: false,
                    pinch: false,
                    touch: false,
                },
                // 시간축 설정
                timeScale: {
                    rightOffset: 3,
                    fixLeftEdge: false,
                    fixRightEdge: false,
                    lockVisibleTimeRangeOnResize: true,
                    barSpacing: 5,
                    minBarSpacing: 2,
                    rightBarStaysOnScroll: true,
                },
            };

            // 차트 인스턴스 생성
            const chartInstance = createChart(container, chartOptions);

            // 차트 크기 자동 조정
            const resizeObserver = new ResizeObserver(() => {
                chartInstance.applyOptions({
                    width: container.clientWidth,
                    height: container.clientHeight,
                });
            });
            resizeObserver.observe(container);

            // 시리즈 설정
            // 1. 캔들스틱
            const candleSeries = chartInstance.addCandlestickSeries({
                upColor: '#ff4444',
                downColor: '#2196f3',
                borderUpColor: '#ff4444',
                borderDownColor: '#2196f3',
                wickUpColor: '#ff4444',
                wickDownColor: '#2196f3',
                priceFormat: {
                    type: 'price',
                    precision: 0,
                    minMove: 1,
                },
            });

            // 2. 거래량
            const volumeSeries = chartInstance.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',
                    precision: 0,
                    formatter: (volume) => {
                        if (volume >= 1000000) {
                            return (volume / 1000000).toFixed(1) + 'M';
                        } else if (volume >= 1000) {
                            return (volume / 1000).toFixed(0) + 'K';
                        }
                        return volume.toString();
                    }
                },
                priceScaleId: 'volume',
            });
            // 거래량 차트의 Y축 설정
            chartInstance.priceScale('volume').applyOptions({
                scaleMargins: {
                    top: 0.7,
                    bottom: 0.05
                },
                visible: true,
                autoScale: true
            });

            // 3. 매출액
            const additionalSeries = chartInstance.addHistogramSeries({
                // color: 'rgba(128, 128, 128, 0.5)',  // 회색 50% 투명도
                color: 'black',
                priceFormat: {
                    type: 'sales',
                    precision: 0,
                    minMove: 1,
                    formatter: ((value) => `${(value / 1000000000000).toFixed(0)}억`),
                },
                priceScaleId: 'sales',
                title: '',
            });
            // 매출액 차트의 Y축 설정
            chartInstance.priceScale('sales').applyOptions({
                scaleMargins: {
                    top: 0.7,
                    bottom: 0.05
                },
                visible: false,
                autoScale: true
            });

            // 시리즈 저장
            charts.set(code, chartInstance);
            candleSeriesMap.set(code, candleSeries);
            volumeSeriesMap.set(code, volumeSeries);
            additionalSeriesMap.set(code, additionalSeries);

            // 리사이즈 이벤트 핸들러
            const handleResize = () => {
                chartInstance.applyOptions({ width: container.clientWidth });
            };
            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('resize', handleResize);
                resizeObserver.disconnect();
            };

        } catch (error) {
            console.error('차트 초기화 실패:', error);
        }
    }

    // 문자열을 숫자로 변환하는 함수
    const stringToNumber = (str) => {
        if (typeof str === 'string') {
            return parseInt(str.replace(/,/g, ''));
        }
        return str;
    };
    
    // 차트 데이터 업데이트 함수
    function updateChartData(data) {

        if (!data || !data.data) return;
        
        
        try {
            const code = stock?.db?.종목코드;
            console.log('차트 데이터 업데이트:', code, data);
            console.log('candleSeriesMap:', candleSeriesMap);
            
            // getQuarterBalanceSheet(code)
            // if (!toggleQuarterChart.includes(code)) {
            //     toggleQuarterChart.push(code);
            // } else {
            //     toggleQuarterChart = toggleQuarterChart.filter(s => s !== code);
            // }
            
            
            const candleSeries = candleSeriesMap.get(code);
            const volumeSeries = volumeSeriesMap.get(code);
            const additionalSeries = additionalSeriesMap.get(code);




            if (!candleSeries || !volumeSeries) {
                console.error('차트 시리즈가 없습니다.');
                return;
            }

            // 데이터 정렬 및 중복 제거
            const uniqueData = new Map();
            data.data.forEach(d => {
                const timeStr = d.날짜.substring(0, 4) + '-' + 
                            d.날짜.substring(4, 6) + '-' + 
                            d.날짜.substring(6, 8);
                uniqueData.set(timeStr, d);
            });

            // 시간순 정렬
            const sortedData = Array.from(uniqueData.entries())
                .sort(([timeA], [timeB]) => new Date(timeA) - new Date(timeB))
                //.slice(-qrycnt);  // 최근 qrycnt개만 사용

            // 캔들 데이터 포맷팅
            const formattedData = sortedData.map(([time, d]) => ({
                time,
                open: Number(d.시가),
                high: Number(d.고가),
                low: Number(d.저가),
                close: Number(d.종가)
            }));

            // 거래량 데이터 포맷팅
            const volumeData = sortedData.map(([time, d]) => ({
                time,
                value: Number(d.거래량),
                color: Number(d.종가) >= Number(d.시가) ? '#ff4444' : '#2196f3'
            }));


            // if (quarterBalance) {
            //     additionalSeries.setData(quarterBalance[code]);
            // }

            if (toggleQuarterChart.includes(code) && $dartData.quarterBalance[code]) {
                // getQuarterBalanceSheet(code);
                console.log('dartData.quarterBalance:', $dartData.quarterBalance);
                const additionalData = $dartData.quarterBalance[code].map(item => {
                    // 객체의 첫 번째 키-값 쌍 추출
                    // console.log('item:', item);
                    const dateStr = item['time'];  // "YYYY-MM-DD" 형식
                    const value = stringToNumber(item['value']);  // 숫자값
                    
                    return {
                        time: dateStr,    // 'YYYY-MM-DD' 형식
                        value: Math.floor(value),      // 소수점 버림림
                        // color: 'rgba(50, 50, 50, 0.5)',  // 막대 회색 50% 투명도
                        // color: 'black',
                        color: 'rgba(0, 0, 0, 1)',  // 막대 회색 50% 투명도
                    };
                });
                // additionalSeries.setData(uniqueData);
                console.log('변환된 예측 데이터:', additionalData);
                additionalSeries.setData(additionalData);
            }
            

            console.log('정렬된 데이터:', formattedData.length, volumeData.length);

            // 데이터 설정
            candleSeries.setData(formattedData);
            volumeSeries.setData(volumeData);


            // 차트 범위 조정
            const chart = charts.get(code);
            if (chart) {
                chart.timeScale().fitContent();
            }

            console.log('차트 데이터 업데이트 완료:', code);
        } catch (error) {
            console.error('차트 데이터 업데이트 실패:', error);
            console.error(error.stack);
        }
    }
    

    // 실시간 차트 업데이트 함수
    function updateRealtimeChart(realData) {

        const code = realData.body.shcode;
        const candleSeries = candleSeriesMap.get(code);
        const volumeSeries = volumeSeriesMap.get(code); 

        // const additionalSeries = additionalSeriesMap.get(code);    // 분기 데이터
        
        if (!candleSeries || !volumeSeries) return;

        // 현재 시간을 ISO 형식으로 변환
        const time = realData.body.chetime;  // "HHMMSS" 형식
        const today = new Date();
        const timeStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

        // 캔들 데이터 업데이트
        const candleData = {
            time: timeStr,
            open: Number(realData.body.open),
            high: Number(realData.body.high),
            low: Number(realData.body.low),
            close: Number(realData.body.price)
        };

        // 거래량 데이터 업데이트
        const volumeData = {
            time: timeStr,
            value: Number(realData.body.volume),
            color: Number(realData.body.price) >= Number(realData.body.open) ? '#ff4444' : '#2196f3'
        };

        // 차트 업데이트
        candleSeries.update(candleData);
        volumeSeries.update(volumeData);

        // 마지막 데이터 저장
        if (!$chartDataStore[code]) {
            $chartDataStore[code] = {
                data: [],
                chartPeriod: chartPeriod
            };
        }
        
        // 새로운 데이터 추가
        $chartDataStore[code].data.push({
            날짜: timeStr.replace(/-/g, ''),
            시가: realData.body.open,
            고가: realData.body.high,
            저가: realData.body.low,
            종가: realData.body.price,
            거래량: realData.body.volume
        });

        // 차트 범위 자동 조정 (선택사항)
        const chart = charts.get(code);
        if (chart) {
            chart.timeScale().fitContent();
        }
    }


    // chartPeriod 변경 처리 함수
    async function updateChartPeriod(code, selected=false) {
        if (!code || !showChart) return;
        
        // 선택된 종목만 차트 표시
        if (selected) {
            $selectedStocks = {};
            $selectedStocks[code] = true;
            $selectedStocks = {...$selectedStocks};
        }
        
        try {
            isLoadingChart = true;
            
            // 새로운 데이터 조회
            await getChartData(code);
            
            // 차트 업데이트
            if ($chartDataStore[code]) {
                updateChartData($chartDataStore[code]);
            }
        } catch (error) {
            console.error('차트 주기 변경 중 오류:', error);
        } finally {
            isLoadingChart = false;
        }
    }

    // qrycnt 변경 감지 및 처리
    $: if (stock && showChart && qrycnt) {
        updateChartPeriod(stock.db.종목코드);
    }

    // 주식차트 조회 차트 그리기 끝////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////// 투자정보 초기화  
    function deleteInvestInfo() {
        // delete $investInfoMap[shcode];
        $investInfoMap = {};
        $selectedStocks = {};
        // $investInfoMap = {...$investInfoMap};  // 반응성 트리거
    }
    // 정보 닫기
    let view_selected_stocks = false;
    function toggleSelectedStocks() {
        $selectedStocks = {};
        $selectedStocks[stock.db.종목코드] = true;
        view_selected_stocks = !view_selected_stocks;
        $selectedStocks = {...$selectedStocks};
    }
        
    // 종목 클릭 시 투자정보 표시
    let stock = null;
    let lastClickedCode = null;
    let lastClickTime = 0;
    const DOUBLE_CLICK_DELAY = 300;  // 더블클릭 판정 시간 (ms)
    // let sortDirection = 1;  // 정렬 방향
    // let isProcessing = false;  // 처리 중 상태 추가
    async function handleStockClick(_code, event) {
        event?.stopPropagation();
        
        
        if (isTest) {   // 테스트 모드일 때 웹소켓 연결 테스트
            getTestWebSocketInfo(_code);
        }
        try {
            if (!$key) return;

            // 더블클릭 처리
            const currentTime = Date.now();
            if (_code === lastClickedCode && (currentTime - lastClickTime) < DOUBLE_CLICK_DELAY) {
                console.log('더블 클릭 감지:', _code);
                sortDirection *= -1;
                $sortedCodes = $sortedCodes.reverse();
                $selectedStocks = {};
                lastClickedCode = null;
                lastClickTime = 0;
                return;
            }
            
            lastClickedCode = _code;
            lastClickTime = currentTime;
            stock = $investInfoMap[_code];

            if (!$selectedStocks[_code]) {
                $selectedStocks[_code] = true;
            } else {
                delete $selectedStocks[_code];
            }
            $selectedStocks = {...$selectedStocks};
            
            
            // 차트 표시 설정
            // 이전 차트 정리
            if (currentChartCode && currentChartCode !== _code) {
                if (charts.has(currentChartCode)) {
                    charts.get(currentChartCode).remove();
                    charts.delete(currentChartCode);
                }
                candleSeriesMap.delete(currentChartCode);
                volumeSeriesMap.delete(currentChartCode);
                chartContainers.delete(currentChartCode);
                additionalSeriesMap.delete(currentChartCode);
            }
            // 차트 표시 설정
            stock = $investInfoMap[_code];
            isLoadingChart = true;
            
            
            if (!showChart) {
                return;
            }
            try {
                // 차트 데이터 확인
                const existingData = $chartDataStore[_code];
                const needsUpdate = !existingData || 
                                (!existingData.chartPeriod) || 
                                (existingData.chartPeriod !== chartPeriod);
                
                console.log('needsUpdate:', needsUpdate);

                if (needsUpdate) {
                    await getChartData(_code);
                }
                // DOM 렌더링 대기
                await new Promise(resolve => setTimeout(resolve, 100));

            } catch (error) {
                console.error('차트 처리 중 오류:', error);
            } finally {
                isLoadingChart = false;
            }

        } catch (error) {
            console.error('종목 클릭 처리 중 오류:', error);
            isLoadingChart = false;
        }
    }



    // //////////////////////////////////////////////////////////////////// 뉴스 데이터 조회
    
    let news = Array(50).fill(null);
    let selectedNews = null;  // 선택된 뉴스 상태 추가
    
    async function getNewsData(realkey) {
        fastapi('get', '/stock/get_news_data', {key: $key, realkey: realkey}, (json) => {
            console.log('뉴스 데이터:', json);
            return json.content;
            // selectedNews = {
            //     ...selectedNews,
            //     content: json.content
            // };
        });
    }

    // 뉴스 아코디언 열기
    let loadingNews = null;  // 로딩 중인 뉴스 추적

    async function toggleNews(item) {
        if (selectedNews === item) {
            selectedNews = null;  // 같은 뉴스 클릭시 닫기
            return;
        }
        
        // 이전에 로딩 중이던 뉴스가 있다면 취소
        if (loadingNews) {
            loadingNews = null;
        }
        
        selectedNews = item;  // 먼저 선택된 뉴스 설정
        
        // content가 없을 때만 API 호출
        if (!item.content) {
            loadingNews = item;  // 현재 로딩 중인 뉴스 설정
            const realkey = item.body.realkey;
            let params = {key: $key, realkey: realkey}
            try {
                fastapi('get', '/stock/get_news_data', params, (json) => {
                    // 현재 선택된 뉴스이고 로딩 중인 뉴스일 때만 content 설정
                    if (selectedNews === item && loadingNews === item) {
                        item.content = json.content;
                    }
                });
            } catch (error) {
                console.error('뉴스 본문 로딩 실패:', error);
                if (selectedNews === item && loadingNews === item) {
                    item.content = '본문을 불러올 수 없습니다.';
                }
            }
        }
    }     
    
        // 뉴스 모달 열기
    function openNewsModal(item) {
        if (item && item.body) {  // item과 body가 존재하는지 확인
            selectedNews = item;
            if (item.body.realkey) {
                console.log('item.body.realkey:', item.body.realkey);
                selectedNews.content = getNewsData(item.body.realkey);
            }
        }
    }

     // HTML 문자열을 안전하게 처리하는 함수
     function sanitizeHtml(html) {
        // 허용할 태그들만 남기고 나머지는 제거
        return html
            .replace(/<\/?(?!p|br|b|strong|em|i|u|ul|ol|li|table|tr|td|th|thead|tbody|img|a)[^>]*>/gi, '') // 허용된 태그만 남김
            .replace(/on\w+="[^"]*"/g, '') // 모든 on* 이벤트 제거
            .replace(/javascript:[^"']*/g, ''); // javascript: 프로토콜 제거
    }

    // 키보드 이벤트 핸들러
    function handleKeyPress(event, item) {
        if (event.key === 'Enter' || event.key === ' ') {
            toggleNews(item);
        }
    }

    // 관심종목 추가
    let showInterestInput = false;  // 입력창 표시 여부
    let newStockCode = '';
    let newStock = null;
    function toggleInterestInput() {
        showInterestInput = !showInterestInput;
        if (!showInterestInput) {
            newStockCode = '';  // 숨길 때 입력값 초기화
        }
    }
    // 관심종목 추가
    function addInterestStock() {
        if (newStockCode && newStockCode.length === 6) {
            // 여기에 관심종목 추가 로직
            console.log('관심종목 추가:', newStockCode);
            const params = {key: $key, code: newStockCode};
            fastapi('post', '/stock/add_interest_stock', params, (json) => {
                console.log('관심종목 추가:', newStockCode);
                newStock = json;
                console.log('newStock:', newStock);
                showInterestInput = false;  // 추가 후 입력창 숨기기
                // console.log('json:', json);
                $investInfoMap[newStockCode] = json[newStockCode];
                $investInfoMap = {...$investInfoMap};
                console.log('investInfoMap:', $investInfoMap);
                newStockCode = '';
            });
        }
    }

// 서치 종목 추가 ////////////////////////////////////////////////////////////////////////////////

    // 검색 결과 저장 변수
    let searchResults = [];
    let searchTimeout;
    let selectedIndex = -1;  // 현재 선택된 아이템의 인덱스
    // 실시간 주식 검색 함수
    async function handleSearchInput(e) {
        const value = e.target.value;
        newStockCode = value;
        
        // 숫자만 입력된 경우
        if (/^\d+$/.test(value)) {
            searchResults = [];
            return;
        }

        // 디바운스 처리
        clearTimeout(searchTimeout);
        if (value.length > 0) {
            searchTimeout = setTimeout(() => {
                searchStocks(value);
            }, 300); // 300ms 디바운스
        } else {
            searchResults = [];
        }
    }

    // API 검색 함수
    async function searchStocks(query) {
        if (!$key) return;
        
        let params = {
            key: $key,
            query: query
        }
        
        fastapi('get', '/stock/search_stocks', params, (json) => {
            console.log('searchResults:', json.stocks);
            searchResults = json.stocks.slice(0, 5); // 최대 5개까지만 표시
        });
    }

    // 검색 결과 선택 함수
    function selectSearchResult(code) {
        newStockCode = code;
        searchResults = [];
    }
    
    function handleKeydown(e, options = {}) {
        const {
            searchResults = [],
            selectedIndex = -1,
            onSelect = () => {},  // 선택 시 실행할 콜백 함수
            onReset = () => {}    // 초기화 시 실행할 콜백 함수
        } = options;

        if (!searchResults.length) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                return { selectedIndex: Math.min(selectedIndex + 1, searchResults.length - 1) };
                
            case 'ArrowUp':
                e.preventDefault();
                return { selectedIndex: Math.max(selectedIndex - 1, 0) };
                
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0) {
                    const selectedStock = searchResults[selectedIndex];
                    onSelect(selectedStock);  // 콜백 실행
                    onReset();  // 초기화 콜백 실행
                }
                break;
                
            case 'Escape':
                onReset();
                break;
        }
    }

    function tradeSearch(e) {
        const result = handleKeydown(e, {
            searchResults,
            selectedIndex,
            onSelect: (stock) => {
                assetCategory = 'stock.krw'
                code = stock.shcode;
                name = stock.shname;
                searchResults = [];
                selectedIndex = -1;
                if (stock.gubun === '1') {
                    market = 'KOSPI';
                } else if (stock.gubun === '2') {
                    market = 'KOSDAQ';
                }
            },
            onReset: () => {
                searchResults = [];
                selectedIndex = -1;
            }
        });

        if (result?.selectedIndex !== undefined) {
            selectedIndex = result.selectedIndex;
        }
    }
    
    
    // 선택 모드 토글 함수
    let codes_select = [];
    let isSelectMode = false;
    function toggleSelectMode() {
        isSelectMode = !isSelectMode;
        if (!isSelectMode) {
            codes_select = [];  // 선택 모드 해제시 선택된 종목 초기화
        }
        console.log('isSelectMode:', isSelectMode);
    }
    
    // 종목 선택 함수 체크박스
    function toggleStockSelection(code) {
        const index = codes_select.indexOf(code);
        if (index === -1) {
            codes_select.push(code);
        } else {
            codes_select.splice(index, 1);
        }
        codes_select = [...codes_select];  // 반응성 트리거
        console.log('toggleStockSelection:', codes_select);
    }

    // 관심종목 삭제
    function deleteInterestStocks() {
        console.log('codes_select:', codes_select);
        let params = {
            codes: codes_select
        }
        fastapi('post', '/stock/delete_interest_stocks'+'?key='+$key, params, (json) => {
            console.log('관심종목 삭제:', json);
            deleteCodes = json.delete_codes;
            for (const code of deleteCodes) {
                delete $investInfoMap[code];
            }
            $investInfoMap = {...$investInfoMap};
        });
    }


    // 관심종목 tag 추가
    // let stock = null; <-- handleStockClick() 함수로 $investInfoMap에서 참조
    let view_selected_stock = false;
    function toggleViewSelectedStock() {
        // console.log('stock:', stock);
        view_selected_stock = !view_selected_stock;
        stock = $investInfoMap[$sortedCodes[0]];
        console.log('view_selected_stock:', view_selected_stock);
    }
    let tag = null;
    function addInterestStockTag() {
        console.log('stock:', stock);
        if (stock && tag && tag.length > 0 && tag !== stock.db.tag) {
            // let code = stock['t3320OutBlock1']['기업코드'].slice(1, 7);
            let code = stock.db.종목코드;
            // let tag = stock.db.tag;
            console.log('code:', code);
            console.log('tag:', tag);
            let params = {
                key: $key,
                code: code,
                tag: tag
            }
            fastapi('post', '/stock/update_interest_stock_tag', params, (json) => {
                console.log('관심종목 tag 추가:', json);
                $investInfoMap[code].db.tag = json.tag;
                $investInfoMap = {...$investInfoMap};
                tag = null;
                stock = null;
            });
        }
    }
    
    function getInvestInfoStock() {
        console.log('getInvestInfoStock:', stock);
        let params = {  
            key: $key,
            code: stock.db.종목코드
        }
        fastapi('get', '/stock/investinfo_t3320', params, (json) => {
            console.log('getInvestInfoStock:', json.investinfo);
            $investInfoMap[stock.db.종목코드].t3320OutBlock = json.investinfo.t3320OutBlock;
            $investInfoMap[stock.db.종목코드].t3320OutBlock1 = json.investinfo.t3320OutBlock1;
            $investInfoMap = {...$investInfoMap};
        });
    }

    function viewInvestInfoStock() {
        // view_selected_stock = true;
        view_selected_stocks = !view_selected_stocks;
        $selectedStocks = {};
        $selectedStocks[stock.db.종목코드] = true;
        // $selectedStocks = {...$selectedStocks};
        // $investInfoMap = {...$investInfoMap};
        // console.log('view_selected_stock:', view_selected_stock);
        // console.log('viewInvestInfoStock:', stock);
        // console.log('selectedStocks:', $selectedStocks);
        // console.log('investInfoMap:', $investInfoMap);
    }

    
    // 종목 정렬
    // 정렬 상태 변수들
    let sortField = null;
    let sortDirection = 1;
    // let sortedCodes = []; // 정렬된 종목코드 배열
    // let lastClickedCode = null;
    // let lastClickTime = 0;

    function sortStocks(field) {
        if (sortField === field) {
            sortDirection *= -1;
        } else {
            sortField = field;
            sortDirection = 1;
        }

        $sortedCodes = Object.keys($investInfoMap).sort((a, b) => {
            // 보유종목은 정렬하지 않고 항상 최상단에 유지
            const aInAccno = accnoCodes.includes(a);
            const bInAccno = accnoCodes.includes(b);
            if (aInAccno || bInAccno) {
                if (aInAccno && bInAccno) {
                    // 보유종목끼리는 원래 순서 유지
                    return accnoCodes.indexOf(a) - accnoCodes.indexOf(b);
                }
                return aInAccno ? -1 : 1;
            }

            let valueA, valueB;
            
            switch(field) {
                case '시가총액':
                    valueA = Number($investInfoMap[a]?.t3320OutBlock?.시가총액 || 0);
                    valueB = Number($investInfoMap[b]?.t3320OutBlock?.시가총액 || 0);
                    break;
                case '외국인':
                    valueA = Number($investInfoMap[a]?.t3320OutBlock?.외국인 || 0);
                    valueB = Number($investInfoMap[b]?.t3320OutBlock?.외국인 || 0);
                    break;
                case '배당수익율':
                    valueA = Number($investInfoMap[a]?.t3320OutBlock?.배당수익율 || 0);
                    valueB = Number($investInfoMap[b]?.t3320OutBlock?.배당수익율 || 0);
                    break;
                case 'PER':
                    valueA = Number($investInfoMap[a]?.t3320OutBlock1?.PER || 0);
                    valueB = Number($investInfoMap[b]?.t3320OutBlock1?.PER || 0);
                    break;
                case 'ROE':
                    valueA = Number($investInfoMap[a]?.t3320OutBlock1?.ROE || 0);
                    valueB = Number($investInfoMap[b]?.t3320OutBlock1?.ROE || 0);
                    break;
                case 'tag':
                    valueA = $investInfoMap[a]?.db?.tag || '';
                    valueB = $investInfoMap[b]?.db?.tag || '';
                    return sortDirection * valueA.localeCompare(valueB);
                case '업종구분명':
                    valueA = $investInfoMap[a]?.db?.업종구분명 || '';
                    valueB = $investInfoMap[b]?.db?.업종구분명 || '';
                    return sortDirection * valueA.localeCompare(valueB);
            }
            return sortDirection * (valueA - valueB);
        });

        return sortedCodes;
    }


    // 컴포넌트 마운트 시와 데이터 변경 시 정렬 유지
    $: {
        if ($investInfoMap && Object.keys($investInfoMap).length > 0) {
            const currentOrder = [...$sortedCodes];
            $sortedCodes = currentOrder.length > 0 ? currentOrder : Object.keys($investInfoMap).sort((a, b) => {
                const aInAccno = accnoCodes.includes(a);
                const bInAccno = accnoCodes.includes(b);
                if (aInAccno && bInAccno) {
                    return accnoCodes.indexOf(a) - accnoCodes.indexOf(b);
                }
                return aInAccno ? -1 : bInAccno ? 1 : 0;
            });
        }
    }

    // 정렬 상태가 변경될 때마다 정렬 실행
    // $: if (sortField || sortDirection) {
    //     sortedCodes = sortStocks(sortField);
    // }


    // 캔들스틱 SVG 생성 함수
    function CandleStick({ candle, width = 20, height = 40 }) {
        if (!candle) return null;
        
        const { open, high, low, close } = candle;
        
        // 캔들의 방향 (상승/하락)
        const isUp = close >= open;
        
        // 값들을 픽셀 좌표로 변환
        const priceRange = high - low;
        const scale = height / (priceRange || 1);
        
        // 좌표 계산
        const wickY1 = (high - high) * scale;
        const wickY2 = (high - low) * scale;
        const bodyY1 = (high - Math.max(open, close)) * scale;
        const bodyY2 = (high - Math.min(open, close)) * scale;
        
        return `
            <svg width="${width}" height="${height}" style="display: inline-block; vertical-align: middle;">
                <!-- 세로 선 (wick) -->
                <line 
                    x1="${width/2}" 
                    y1="${wickY1}" 
                    x2="${width/2}" 
                    y2="${wickY2}" 
                    stroke="${isUp ? '#ff4444' : '#2196f3'}" 
                    stroke-width="1"
                />
                <!-- 캔들 몸통 (body) -->
                <rect 
                    x="${width/4}" 
                    y="${bodyY1}" 
                    width="${width/2}" 
                    height="${Math.max(1, bodyY2 - bodyY1)}" 
                    fill="${isUp ? '#ff4444' : '#2196f3'}"
                    stroke="${isUp ? '#ff4444' : '#2196f3'}"
                />
            </svg>
        `;
    }

//


// 직접 웹소켓 연결 /////////////////////////////////////////////////////////////////////////////////////////
    
const WS_STATUS = {
    0: 'CONNECTING',  // 연결 중
    1: 'OPEN',       // 연결됨
    2: 'CLOSING',    // 종료 중
    3: 'CLOSED'      // 종료됨
};

// 종료 코드 설명
const WS_CLOSE_CODES = {
    1000: '정상 종료',
    1001: '서버/클라이언트 종료',
    1002: '프로토콜 에러',
    1003: '데이터 타입 에러',
    1005: '상태 코드 없음',
    1006: '비정상 종료',
    1007: '데이터 타입 불일치',
    1008: '정책 위반',
    1009: '메시지가 너무 큼',
    1010: '확장 협상 실패',
    1011: '서버 에러',
    1015: 'TLS 핸드쉐이크 실패'
};



let isDirectWss = false;
    // WebSocket 연결들을 저장할 Map
    const wsConnections = writable(new Map());  // key: 연결 식별자, value: WebSocket 객체
    
    // WebSocket 연결 추가 함수
    function addWebSocketConnection(type, ws) {
        wsConnections.update(connections => {
            const newConnections = new Map(connections);
            newConnections.set(type, ws);
            return newConnections;
        });
        console.log('WebSocket 연결 추가:', type);
    }

    // 특정 연결만 종료하는 예시
    function stopNewsOnly() {
        closeDirectWss('news');
    }

    // 특정 연결의 상태 확인
    function isConnected(type = 'direct') {
        let connections;
        wsConnections.subscribe(value => {
            connections = value;
        })();

        const ws = connections.get(type);
        return ws && ws.readyState === WebSocket.OPEN;
    }

    // 웹소켓 연결 종료 함수 수정
    function closeDirectWss(type = 'direct') {
        wsConnections.update(connections => {
            const newConnections = new Map(connections);
            const ws = newConnections.get(type);
            if (ws) {
                // 연결 상태 확인
                if (ws.readyState === WebSocket.OPEN || 
                    ws.readyState === WebSocket.CONNECTING) {
                    
                    // onclose 이벤트 핸들러 추가
                    ws.onclose = (event) => {
                        console.log(`WebSocket ${type} 연결 종료:`, {
                            code: event.code,
                            reason: event.reason,
                            wasClean: event.wasClean ? '정상 종료' : '비정상 종료',
                            timestamp: new Date().toLocaleString()
                        });
                    };
                    
                    // onerror 이벤트 핸들러 추가
                    ws.onerror = (error) => {
                        console.error(`WebSocket ${type} 종료 중 에러:`, {
                            error: error,
                            timestamp: new Date().toLocaleString()
                        });
                    };

                    try {
                        ws.close(1000, "사용자 요청으로 정상 종료");  // 종료 이유 추가
                        console.log(`WebSocket ${type} 종료 요청 전송`);
                    } catch (error) {
                        console.error(`WebSocket ${type} 강제 종료:`, {
                            error: error,
                            timestamp: new Date().toLocaleString()
                        });
                    }
                } else {
                    console.log(`WebSocket ${type} 상태:`, {
                        readyState: ws.readyState,
                        stateText: ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][ws.readyState],
                        timestamp: new Date().toLocaleString()
                    });
                }
                
                // Map에서 제거
                newConnections.delete(type);
                console.log(`WebSocket ${type} Map에서 제거됨`);
            } else {
                console.log(`WebSocket ${type} 연결을 찾을 수 없음`);
            }
            return newConnections;
        });

        // 상태 업데이트
        isDirectWss = false;
        console.log('WebSocket 전역 상태 업데이트: isDirectWss =', isDirectWss);
    }

    // 모든 웹소켓 연결 종료 함수 추가
    function closeAllConnections() {
        wsConnections.update(connections => {
            connections.forEach((ws, type) => {
                if (ws) {
                    try {
                        ws.close(1000, "Normal Closure");
                    } catch (error) {
                        console.error(`${type} 연결 종료 실패:`, error);
                    }
                }
            });
            return new Map();  // 빈 Map으로 초기화
        });
        isDirectWss = false;
    }

    // 토큰 발급 함수
    async function getToken() {
        let params = {
            key: $key
        }
        return new Promise((resolve, reject) => {
            fastapi('get', '/stock/get_token', params, (json) => {
                resolve(json.token);
            });
        });
    }
    
    async function directWss() {
        if (!browser) return null;

        // 이미 연결이 있다면 먼저 종료
        closeDirectWss('direct');

        try {
            const token = await getToken();
            const BASE_URL = 'wss://openapi.ls-sec.co.kr:9443/websocket';
            console.log('연결 시도:', BASE_URL);
            
            const directWss = new WebSocket(BASE_URL);
            
            directWss.onopen = () => {
                console.log('WebSocket 연결됨');
                isDirectWss = true;
                addWebSocketConnection('direct', directWss);
                
                // 뉴스 구독
                const newsHeader = {
                    "token": token,
                    "tr_type": "3"
                };
                const newsBody = {
                    "tr_cd": "NWS",
                    "tr_key": "NWS001"
                };
                directWss.send(JSON.stringify({ header: newsHeader, body: newsBody }));
                
                // 각 종목 코드에 대한 실시간 주가 구독
                for (let code of Object.keys($investInfoMap)) {
                    const marketType = $investInfoMap[code].db.시장구분;
                    if (marketType === '1' || marketType === '2') {
                        const header = {
                            "token": token,
                            "tr_type": "3"  // 실시간 주가는 tr_type이 1
                        };
                        const body = {
                            "tr_cd": marketType === '1' ? 'S3_' : 'K3_',
                            "tr_key": code
                        };
                        const message = JSON.stringify({ header, body });
                        // console.log('주가 구독 요청:', message);
                        directWss.send(message);
                    }
                }
            };
            
            directWss.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.body) {
                        handleWebSocketMessage(data);   // 뉴스, 주가 데이터 처리
                        
                    }else if (data.header.rsp_cd == '00000') {
                        console.log(data.header.tr_cd, data.header.rsp_msg);  // 전체 메시지 로깅
                    }else{
                        console.log(data);  // 전체 메시지 로깅
                    }
                } catch (error) {
                    console.error('메시지 처리 오류:', error);
                }
            };

            directWss.onclose = () => {
                console.log('WebSocket 연결 종료');
                isDirectWss = false;
                wsConnections.update(connections => {
                    const newConnections = new Map(connections);
                    newConnections.delete('direct');
                    return newConnections;
                });
            };
        } catch (error) {
            isDirectWss = false;
            console.error('WebSocket 연결 실패:', error);
        }
    }

    // 웹소켓 메시지 처리 함수 수정
    function handleWebSocketMessage(data) {
        // console.log('handleWebSocketMessage:', data);
        try {
            // 뉴스 데이터 처리
            if (data.header['tr_cd'] == 'NWS') {
                // console.log('handleNewsMessage:', data.header);
                handleNewsMessage(data);
            } 
            // 주가 데이터 처리
            else if (data.header['tr_cd'] == 'S3_' || data.header['tr_cd']=='K3_' ||data.header['tr_cd']=='s3_') {
                handleStockPriceMessage(data);  // $investInfoMap 업데이트
                
                updateRealtimeChart(data);      // 실시간 차트 업데이트
            }
        } catch (error) {
            console.error('메시지 처리 오류:', error);
        }
    }

    // 뉴스 메시지 처리
    let lastNewsId = null;
    function handleNewsMessage(data) {
        // console.log('handleNewsMessage:', data);
        const currentNewsId = data.body.realkey;
        // 중복 체크: 마지막 뉴스와 다른 경우에만 추가
        if (currentNewsId !== lastNewsId) {
            news = [data, ...news.slice(0, 49)];
            lastNewsId = currentNewsId;  // 마지막 뉴스 ID 업데이트
        }
    }

    // 주가 메시지 처리
    function handleStockPriceMessage(data) {
        const shcode = data.body.shcode;
        
        // 보유종목 업데이트
        if ($accno_codes.includes(shcode)) {
            updateAccnoList(data);
        }
        
        // 관심종목 업데이트
        if ($investInfoMap[shcode]) {
            updateInvestInfo(data);
            
            // 캔들 데이터 업데이트
            $candleStore[shcode] = {
                open: Number(data.body.open),
                high: Number(data.body.high),
                low: Number(data.body.low),
                close: Number(data.body.price)
            };
            
            // 반응성 트리거를 위한 재할당
            $candleStore = { ...$candleStore };
        }
    }

    // 보유종목 데이터 업데이트
    function updateAccnoList(data) {
        console.log('updateAccnoList data:', data);
        console.log('updateAccnoList $accno_codes:', $accno_codes);
        console.log('updateAccnoList $accno_list:', $accno_list);
        const index = $accno_codes.indexOf(data.body.shcode) + 3;
        const peyonga = $accno_list[index][23];
        const peyongason = $accno_list[index][24];
        
        // 개별 종목 정보 업데이트
        $accno_list[index][22] = data.body.price;
        console.log('updateAccnoList $accno_list[index][22]:', data.body.price, index);
        $accno_list[index][23] = $accno_list[index][2] * $accno_list[index][22];    // 평가 금액
        $accno_list[index][24] = $accno_list[index][23] - $accno_list[index][5];    // 평가 손익
        $accno_list[index][25] = ($accno_list[index][24] / $accno_list[index][5] * 100).toFixed(1); // 수익률
        $accno_list[index][26] = Math.floor($accno_list[index][23] * 0.00015);  // 수수료
        $accno_list[index][27] = Math.floor($accno_list[index][23] * 0.0003);   // 제세금
        
        // 총계 업데이트
        $accno_list[1][5] = $accno_list[1][5] - peyonga + $accno_list[index][23];   // 총 평가 금액
        $accno_list[1][0] = $accno_list[1][5] + $accno_list[1][3];  // 총 평가 손익
        $accno_list[1][1] = $accno_list[1][1] - peyongason + $accno_list[index][24];  // 총 수수료 + 제세금
    }

    // 관심종목 데이터 업데이트
    function updateInvestInfo(data) {
        const shcode = data.body.shcode;
        $investInfoMap[shcode].t8407OutBlock1.현재가 = data.body.price;
        $investInfoMap[shcode].t8407OutBlock1.등락율 = data.body.drate;
        $investInfoMap[shcode].t8407OutBlock1.누적거래량 = data.body.volume;
        $investInfoMap[shcode].t8407OutBlock1.체결수량 = data.body.cgubun == '-' ? -data.body.cvolume : data.body.cvolume;
        $investInfoMap[shcode].wss = data.body;
        $investInfoMap = {...$investInfoMap};  // 반응성 트리거
    }
// 

//// 테스트 웹소켓 연결  /////////////////////////////////////////////////////////////////////////////////////////

    let ws = null;
    // let isConnected = false;
    let isTest = false;

    // 테스트 모드 토글 시 WebSocket 처리
    function toggleTest() {
        isTest = !isTest;
        if (isTest) {
            view_selected_stock = true;
            // 첫 번째 종목 코드 가져오기
            const firstCode = Object.keys($investInfoMap)[0];
            stock = $investInfoMap[firstCode];
            console.log('toggleTest stock:', stock);
            console.log('toggleTest investInfoMap:', $investInfoMap);
        } else {
            view_selected_stock = false;
            // 테스트 모드 종료 시 WebSocket 연결도 종료
            closeDirectWss('test');
        }
    }

    async function getTestWebSocketInfo(code) {

        stock = $investInfoMap[code];
        console.log('getTestWebSocketInfo code:', code);
        console.log('getTestWebSocketInfo stock:', $investInfoMap[code]);
        console.log('getTestWebSocketInfo showChart:', showChart);
        console.log('getTestWebSocketInfo stock:', stock);
        // 차트 초기화 및 표시
        if (showChart) {
            // isLoadingChart = true;
            try {
                // 차트 데이터가 없거나 주기가 다른 경우 새로 조회
                const existingData = $chartDataStore[code];
                const needsUpdate = !existingData || 
                                (existingData.chartPeriod !== chartPeriod);
                
                if (needsUpdate) {
                    await getChartT8410(code);
                }

                // DOM 업데이트 대기
                await new Promise(resolve => setTimeout(resolve, 100));

                // 차트 초기화 및 데이터 표시
                if (chartContainers.get(code)) {
                    await initializeChart(code);
                    updateChartData($chartDataStore[code]);
                }
            } catch (error) {
                console.error('차트 처리 중 오류:', error);
            } finally {
                // isLoadingChart = false;
            }
        }

        // 웹소켓 연결
        console.log('getTestWebSocketInfo stock:', code);
        let tr_cd = '';
        if ($investInfoMap[code].db.시장구분 == '1') {
            tr_cd = 'S3_';
        }else if ($investInfoMap[code].db.시장구분 == '2') {
            tr_cd = 'K3_';
        }
        // const code = stock.db.종목코드;
        
        let params = {
            key: $key,
            tr_cd: tr_cd,
            code: code,
        }
        
        fastapi('get', '/stock/test_ws-info', params, (json) => {
            console.log('테스트 웹소켓 정보:', json);
            let url = json.websocket_url;
            console.log('테스트 웹소켓 정보:', url);
            connectTestWebSocket(url);
        });

    }

    async function connectTestWebSocket(url) {
        // 기존 연결이 있다면 종료
        if (isConnected('test')) {
            closeDirectWss('test');
        }

        try {
            // WebSocket 연결
            url = import.meta.env.VITE_WSS_URL + url;
            console.log('WebSocket url:', url);

            const testWss = new WebSocket(url);
            let isAuthenticated = false;

            // 웹소켓 연결 이벤트 처리
            testWss.onopen = () => {
                console.log('WebSocket 연결됨:', url);
                // addWebSocketConnection('test', testWss);
                testWss.send(JSON.stringify({
                    type: 'auth',
                    token: $access_token
                }));
            };

            testWss.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    // 인증 응답 처리
                    if (data.type === 'auth_response') {
                        if (data.status === 'success') {
                            isAuthenticated = true;
                            console.log('인증 성공');
                            addWebSocketConnection('test', testWss);
                        } else {
                            console.error('인증 실패:', data.message);
                            testWss.close();
                        }
                        return;
                    }

                    // 인증된 상태에서만 다른 메시지 처리
                    if (isAuthenticated) {
                        handleWebSocketMessage(data);
                    }
            } catch (error) {
                console.error('메시지 파싱 오류:', error);
            }
        };

            testWss.onclose = () => {
                console.log('WebSocket 연결 종료:', event.code, event.reason);
                isAuthenticated = false;
                // 재연결 로직 추가 가능
                // setTimeout(() => connectTestWebSocket(url), 5000);
            };

            testWss.onerror = (error) => {
                console.error('WebSocket 오류:', error);
                isAuthenticated = false;
            };
            
        } catch (error) {
            console.error('WebSocket 연결 실패:', error);
        }
    }


    // 실시간 데이터로 차트 업데이트
    function updateChartWithRealData(data) {
        if (!data || !data.body) return;

        console.log('updateChartWithRealData:', data);
        const price = Number(data.body.price);
        const volume = Number(data.body.volume);
        const time = data.body.chetime;  // "HHMMSS" 형식
        
        updateRealtimeChart(data);

        // 차트 업데이트 로직
        // ...
    }


    // 선택된 상세 정보 표시를 위한 상태 변수 수정
    let selectedDetail = {
        field: null,
        label: null  // 표시될 레이블 추가
    };

    // 상세 정보 클릭 핸들러 수정
    function handleDetailClick(field) {
        let label;
        switch(field) {
            case '시가총액':
                label = '시총';
                break;
            case '외국인':
                label = '외인';
                break;
            case '배당수익율':
                label = '배당';
                break;
            case 'PER':
            case 'ROE':
                label = field;
                break;
            case 'tag':
                label = '태그';
                break;
            case '업종구분명':
                label = '업종';
                break;
        }
        selectedDetail = { field, label };
        sortStocks(field);
    }

    // 값 표시를 위한 헬퍼 함수
    function getDetailValue(code, field) {
        switch(field) {
            case '시가총액':
                return formatNumber($investInfoMap[code]?.t3320OutBlock?.시가총액 || 0);
            case '외국인':
                return $investInfoMap[code]?.t3320OutBlock?.외국인 || 0;
            case '배당수익율':
                return $investInfoMap[code]?.t3320OutBlock?.배당수익율 || 0;
            case 'PER':
                return $investInfoMap[code]?.t3320OutBlock1?.PER || 0;
            case 'ROE':
                return $investInfoMap[code]?.t3320OutBlock1?.ROE || 0;
            case 'tag':
                return $investInfoMap[code]?.db?.tag || '';
            case '업종구분명':
                return $investInfoMap[code]?.db?.업종구분명 || '';
            default:
                return code;
        }
    }

//


// 매매일지 시작 /////////////////////////////////////////////////////////////////////////////////////////
    // 선택 가능한 항목 정의
    const detailOptions = [
        { value: '', label: '코드' },
        { value: '시가총액', label: '시총' },
        { value: '외국인', label: '외인' },
        { value: '배당수익율', label: '배당' },
        { value: 'PER', label: 'PER' },
        { value: 'ROE', label: 'ROE' },
        { value: 'tag', label: '태그' },
        { value: '업종구분명', label: '업종' }
    ];

    
    // 입력 폼 상태 관리
    let isTradeLog = false; // 매매일지 토글
    let isEditTrade = false; // 편집 토글
    let date = new Date().toISOString().split('T')[0];
    let assetCategory = '';  // stock, crypto, cash
    let market = '';  // KOSPI, KOSDAQ, NASDAQ, USD, KRW, 암호화폐
    let code = '';      // 종목코드 042700 AAPL, BTC, USD, KRW
    let name = '';
    let amount = null;
    let price = null;
    // let dividend = null;
    let quantity = null;
    let quantity0 = null;
    let quantity1 = null;
    let quantity2 = null;
    let price0 = null;
    let price1 = null;
    let price2 = null;
    let fee = null;
    let tax = null;
    let action = '';  // in, out
    let memo = '';

    let trade_id = null;
    // let username = '';

    // 태그 조회
    let trade_tag = {};
    // let assetCategories = [];   // stock, crypto, cash
    let assetCategories = [
        { value: 'stock', label: '주식,기타', trades: []},
        { value: 'stock,dividend', label: '배당', trades: []},
        { value: 'cash', label: '현금', trades: [] },
        { value: 'exchange', label: '환전', trades: [] },

    ];  
    // 매매일지 토글
    function toggleTradeLog() {
        getTradeAlltags();
        isTradeLog = !isTradeLog;
    }
    // 편집 토글
    function toggleEditTrade() {
        
        if (isEditTrade) {
            clearTradeLog();
        }
        isEditTrade = !isEditTrade;
    }
    
    // 거래 유효성 검사
    function validateTradeLog() {
        const errors = [];
        // 공통 검증
        if (!date) errors.push('날짜를 입력하세요');
        if (!action) errors.push('거래 유형을 선택하세요');
        if (!assetCategory) errors.push('자산 구분을 선택하세요');
        // 주식, 가상화폐 검증
        if (!assetCategory.includes('cash') && 
            !assetCategory.includes('exchange') && 
            !assetCategory.includes('dividend')) {
            if (!code) errors.push('종목코드를 입력하세요');
            if (!market) errors.push('시장을 선택하세요');
            if (!name) errors.push('종목명을 입력하세요');
            if (!price) errors.push('가격을 입력하세요');
            if (!quantity) errors.push('수량을 입력하세요');
            if (!amount) errors.push('금액을 입력하세요');
        }
        else if (assetCategory.includes('cash')) {
            if (!code) errors.push('통화를 선택하세요');
            if (!amount) errors.push('금액을 입력하세요');
        }
        else if (assetCategory.includes('exchange')) {
            if (!name) errors.push('외화를 입력하세요');
            if (!code) errors.push('원화를 입력하세요');
            if (!quantity) errors.push('외화 금액을 입력하세요');
            if (!price) errors.push('환율을 입력하세요');
            if (!amount) errors.push('원화 금액을 입력하세요');
        }else if (assetCategory.includes('dividend')) {
            if (!date) errors.push('날짜를 입력하세요');
            if (!action) errors.push('거래 유형을 선택하세요');
            if (!assetCategory) errors.push('자산 구분을 선택하세요');
            if (!code) errors.push('종목코드를 입력하세요');
            if (!market) errors.push('시장을 선택하세요');
            // if (!dividend) errors.push('배당금을 입력하세요');
        }
        return errors;
    }
    // 거래 추가 함수
    function addTrade() {
        let trade_log = {};
        // 유효성 검사
        const errors = validateTradeLog(assetCategory, trade_log);
        
        if (assetCategory.includes('dividend')) {
            trade_log = {
                date: date,
                asset_category: assetCategory,  // stock, crypto, cash, exchange
                market: market,
                code: code,
                name: name,
                amount: amount,
                fee: fee,
                tax: tax,
                action: action,
                memo: memo,
            }
            fastapi('post', '/stock/dividend_log', trade_log, (json) => {
                console.log('배당 거래 로그:', json);
                // 성공 시에만 폼 초기화
                clearTradeLog();
                // assetCategory = 'stock';
                // dividend = null;
                fetchTrades();

            });
        }

        if (!assetCategory.includes('cash') && !assetCategory.includes('exchange') && !assetCategory.includes('dividend')) {
            // 주식 거래 추가
            trade_log = {
                date: date,
                asset_category: assetCategory,  // stock, crypto, cash, exchange
                market: market,  // KOSPI, KOSDAQ, NASDAQ, USD, KRW, 암호화폐
                code: code,
                name: name,
                price: price,
                quantity: quantity,
                fee: fee,
                tax: tax,
                amount: amount,
                action: action,
                memo: memo,
            }
            console.log('addTrade trade_log:', trade_log);
            fastapi('post', '/stock/trade_log', trade_log, (json) => {
                console.log('주식 거래 로그:', json);
                // 성공 시에만 폼 초기화
                clearTradeLog();
                assetCategory = 'stock';
                fetchTrades();
            });
           
        } else if (assetCategory.includes('cash')) {
            
            // 현금 거래 추가
            let transaction = {
                date: date,
                asset_category: assetCategory,  // stock, crypto, cash, exchange
                code: code,
                name: name,
                amount: amount,
                action: action,
                fee: fee,
                tax: tax,
                memo: memo,
            }
            console.log('addTrade transaction:', transaction);
            fastapi('post', '/stock/transaction_log', transaction, (json) => {
                console.log('주식 거래 로그:', json);
                // 성공 시에만 폼 초기화
                clearTradeLog();
                assetCategory = 'cash';
            });
        } else if (assetCategory.includes('exchange')) {
        
            // 환전 거래 추가
            let exchange = {
                date: date,
                asset_category: assetCategory,  // stock, crypto, cash, exchange
                code: code,   // 환전받을 통화
                name: name,   // 환전할 통화
                quantity: quantity, // 환전할 금액
                price: price,    // 환율
                amount: amount,   // 환전받을 금액
                action: action,
                memo: memo,
            }
            console.log('addTrade exchange:', exchange);
            fastapi('post', '/stock/exchange_log', exchange, (json) => {
                console.log('주식 거래 로그:', json);
                // 성공 시에만 폼 초기화
                clearTradeLog();
                assetCategory = 'exchange';
                fetchTrades();
            });
        }
        
        
        if (errors.length > 0) {
            // 에러 메시지 표시
            alert(errors.join('\n'));
            return;
        }
        // 입력 폼 초기화
        // name = '';
        // code = '';
        // action = '';
        // memo = '';
        // assetCategory = '';
        // market = '';
        // action = '';        
        // quantity = null;
        // price = null;
        // amount = null;
        // dividend = null;
        // fee = null;
        // tax = null;
        // fetchTrades();
    }

    // id로 거래 삭제
    function deleteTrade(id) {

        // 경고 메시지 표시
        console.log('deleteTrade id:', id);
        if (confirm('정말로 삭제하시겠습니까?')) {
            fastapi('delete', '/stock/trade_log', {id: id}, (json) => {
                console.log('거래 삭제:', json);
                fetchTrades();
            });
        }
    }


    // 거래 수정값 변수에 입력
    function tradeEdit(id) {
        console.log('tradeEdit id:', id);
        console.log('tradeEdit trade_log:', trades);
        let edit_trade = trades.find(trade => trade.id === id);
        
        console.log('edit_trade:', edit_trade);
        trade_id = id;
        date = edit_trade.date;
        name = edit_trade.name;
        code = edit_trade.code;
        assetCategory = edit_trade.asset_category;
        market = edit_trade.market;
        action = edit_trade.action;
        quantity = edit_trade.quantity;
        price = edit_trade.price;
        // dividend = edit_trade.dividend;
        amount = edit_trade.amount;
        fee = edit_trade.fee || null;
        tax = edit_trade.tax || null;
        // username = edit_trade.username;
        memo = edit_trade.memo;
    }
    // 거래 수정
    function updateTrade(id) {
        console.log('updateTrade');
        let trade_log = {
            id: id,
            date: date,
            name: name,
            code: code,
            asset_category: assetCategory,
            market: market,
            action: action,
            quantity: quantity,
            // dividend: dividend,
            price: price,
            amount: amount,
            fee: fee,
            tax: tax,
            username: $username,
            memo: memo,
        }
        // if (assetCategory.includes('dividend')) {
        //     trade_log.amount = dividend;
        // }
        console.log('updateTrade trade_log:', trade_log);
        fastapi('put', '/stock/trade_log', trade_log, (json) => {
            console.log('거래 수정:', json);
            clearTradeLog();
            isEditTrade = false;
            fetchTrades();
        });
    }

    let assetCategory_sub = [];
    // 자산 구분 선택
    function selectAssetCategory(subCategory) {
        console.log('assetCategory:', assetCategory);
        console.log('trade_tag.currencies:', trade_tag.currencies);
        const category = (assetCategory+',').split(',')[0];
        const currency = ('test,'+assetCategory).split(',').slice(-1)[0];
        const origin_subCategory = assetCategory.replace(category, '').replace(currency, '').replace(',,', ',').replace(/^\,|\,$/g, '');
        console.log('origin_subCategory:', origin_subCategory);
        if (origin_subCategory == subCategory) {
            assetCategory = assetCategory.replace(','+subCategory, '');
            return;
        }
        console.log('origin_subCategory:', origin_subCategory);
        console.log('currency:', currency);
        if (trade_tag.currencies.includes(currency)) {
            assetCategory = category + ',' + subCategory + ',' + currency;
        }else {
            assetCategory = category + ',' + subCategory;
        }
        // console.log('category:', category);
        // try {
        //     if (!assetCategory.includes(subCategory)) {
        //         assetCategory = assetCategory.split(',');
        //         assetCategory.splice(1, 0, subCategory);
        //         assetCategory = assetCategory.join(',');
        //         assetCategory = assetCategory.replace(/,$/, '');
        //     } else {
        //         assetCategory = assetCategory.replace(subCategory, '');
        //         assetCategory = assetCategory.replace(',,', ',');
        //         assetCategory = assetCategory.replace(/,$/, '');
        //     }

        // } catch (error) {
        //     assetCategory = assetCategory + ',' + subCategory;
        //     assetCategory = assetCategory.replace(/,$/, '');
        //     assetCategory = assetCategory.replace(',,', ',');
        // }
        console.log('assetCategory:', assetCategory);
    }
    // 통화 선택
    function selectCurrency(currency, edit = false) {
        console.log('selectCurrency currency:', currency);
        let currency_tag = '';
        try {
            currency_tag = trade_tag.currencies.find(currency => currency === assetCategory.split(',').at(-1));
        } catch (error) {
            currency = null;
        }
        if (!currency_tag) {
            assetCategory = [assetCategory, currency].join(',');
            // assetCategory = assetCategory.replace(/,$/, '');
            // assetCategory = assetCategory.replace(',,', ',');
        } else if (assetCategory.includes(currency) && !edit) {
            assetCategory = assetCategory.replace(','+currency, '');
            // assetCategory = assetCategory.replace(/,$/, '');
            // assetCategory = assetCategory.replace(',,', ',');
        } else {
            assetCategory = assetCategory.replace(currency_tag, currency);
        }
        assetCategory = assetCategory.replace(/,$/, '');
        assetCategory = assetCategory.replace(',,', ',');
        console.log('assetCategory:', assetCategory);
    }
    // 입력 폼 초기화   
    function clearTradeLog() {
        name = '';  // 종목명
        // code = '';  // 종목코드
        memo = '';  // 메모
        // assetCategory = '';  // stock, crypto, cash, exchange
        market = '';  // KOSPI, KOSDAQ, NASDAQ
        action = '';  // in, out
        quantity = null;
        amount = null;
        fee = null;
        tax = null;
        price = null;
        // dividend = null;
        price0 = null;
        price1 = null;
        price2 = null;
        quantity0 = null;
        quantity1 = null;
        quantity2 = null;
    }
    function resetTradeLog() {
        name = '';  // 종목명
        code = '';  // 종목코드
        market = '';  // KOSPI, KOSDAQ, NASDAQ
        action = '';  // in, out
        quantity = null;
        price = null;
        amount = null;
        fee = null;
        tax = null;
        if (assetCategory.includes('dividend')) {
            action = 'in';  // in, out
        } else if (!assetCategory.includes('cash') && !assetCategory.includes('exchange')) {
            name = '';  // 종목명
            code = '';  // 종목코드
            market = '';  // KOSPI, KOSDAQ, NASDAQ
            action = '';  // in, out
            quantity = null;
            price = null;
            amount = null;
        } else if (assetCategory.includes('cash')) {
            code = 'KRW';  // 통화
            amount = null;  // 금액
            action = '';  // in, out
        } else if (assetCategory.includes('exchange')) {
            name = 'USD';   // 환전할 통화
            code = 'KRW';   // 환전받을 통화
            quantity = null; // 환전할 금액
            price = null;    // 환율
            amount = null;   // 환전받을 금액
            action = '';  // in, out
        }
        $trade_keyword = {};
        fetchTrades();
        getTradeAlltags();
    }


    
    // 페이지네이션 추가 /////////////////////////////////////////////////////////////////////////////////////////
    // 페이지네이션 변수 선언
    let paginatedTrades = []; // 페이지네이션된 데이터를 저장할 변수 추가
    // let currentPage = 1;
    let itemsPerPage = 10;
    let totalItems = 0;
    // let totalPages = 0;
    let trades = []; // 전체 거래 데이터
    let startDate = '';
    let endDate = '';
    // let tradeAssetCategories = [];
    // let badgeAssetCategory = [];
    async function loadTransactions(page = 1) {
        try {
            const response = await fetch(
                API_BASE_URL + `/stock/investments/transactions?page=${page}&limit=${$investmentStore.pagination.itemsPerPage}`
            );
            const data = await response.json();
            investmentStore.setTransactions(data.items);
            investmentStore.setTotalItems(data.total);
            investmentStore.setPage(page);
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }
    // 거래 데이터 조회
    async function fetchTrades(trade_code = null) {
        console.log('fetchTrades $trade_keyword:', $trade_keyword);
        try {
            let params = {
            skip: (currentPage - 1) * itemsPerPage,
                limit: itemsPerPage,
            };
            if (Object.keys($trade_keyword).length > 0) {
                params = { ...params, ...$trade_keyword };
            }
            // if (assetCategory) {
            //     params.asset_category = assetCategory;
            // }
            
            console.log('fetchTrades params:', params);
        // 선택적 파라미터들은 값이 있을 때만 추가
            // if (trade_code) params.code = trade_code;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        if (assetCategory) params.asset_category = assetCategory;
            // $trade_keyword.set(params);
            // console.log('fetchTrades params:', params);
            fastapi('get', '/stock/trade_log', params, (json) => {
                trades = json.items; // 페이지네이션된 거래 데이터
                console.log('fetchTrades trades:', trades);
                totalItems = json.total; // 전체 거래 수
                totalPages = Math.ceil(totalItems / itemsPerPage); // 전체 페이지 수
            });
        } catch (error) {
            console.error('Error fetching trades:', error);
        }
    }
    async function getTradeAlltags() {
        await fastapi('get', '/stock/trades/all_tags', {}, (json) => {
            trade_tag = json;
            console.log('trade_tag:', trade_tag);
        });
    }

    function searchByCode(code) {
        $trade_keyword.code = code;
        fetchTrades();
    }
    // assetCategory가 변경될 때마다 데이터 다시 로드
    $: {
        
        if (assetCategory){
            fetchTrades();
        }

        if (assetCategory.includes('exchange') && action == 'in' && quantity && price) {
            amount = Math.trunc(Math.abs(quantity * price) * -1);
        }
        if (assetCategory.includes('exchange') && action == 'out' && quantity && price) {
            amount = Math.trunc(Math.abs(quantity * price));
        }
        

        if (quantity0 || quantity1 || quantity2 ) {
            if (assetCategory.includes('stock')) {
                // 소수점 두번째 자리 절삭
                quantity = quantity0 + quantity1 + quantity2;
                amount = price0*quantity0 + price1*quantity1 + price2*quantity2;
                price = Math.floor(100 * amount / quantity) / 100;
                price = Math.abs(price);
                if (action === 'out') {
                    amount = Math.abs(amount);
                    quantity = Math.abs(quantity) * -1;
                } else if (action === 'in') {
                    amount = Math.abs(amount) * -1;
                    quantity = Math.abs(quantity);
                }
            }
        }
        if (amount) {
            let feeTax = calculateFeeTax(assetCategory, code, action, amount);
            fee = feeTax.fee;
            tax = feeTax.tax;
        }
        if (assetCategory) {
            // assetCategory = assetCategory.split(',')[0];
        currentPage = 1;
            console.log('currentPage:', currentPage);
            // fetchTrades();
        }
        // if (trade_tag) {
        //     // 태그 데이터 추출 badgeAssetCategory 에 없으면 추가
        //     if (Array.isArray(trade_tag.asset_categories)) {   
        //         for (let i = 0; i < trade_tag.asset_categories.length; i++) {

        //             let tag = trade_tag.asset_categories[i].replace('.', ',');
        //             tag = tag.split(',').slice(0, 2);
                    
        //             if (tag[1]) {tag = tag[0] + ',' + tag[1];}
        //             else {tag = tag[0];}
                    
        //             if (!badgeAssetCategory.includes(tag)) {
        //                 badgeAssetCategory.push(tag);
        //             }
                    
        //         }
        //     }
        //     console.log('badgeAssetCategory:', badgeAssetCategory);
        // }
    }

    // 페이지네이션 추가 끝 /////////////////////////////////////////////////////////////////////////////////////////
    
    // 종목명 클릭시 버튼 컴퍼넌트 표시
    let taxData = null;

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

// investment 페이지 /////////////////////////////////////////////////////////////////////////////////////////
    const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('http://', 'https://') || 'https://api2410.ebesesk.synology.me';
    let transactions = [];
    let assets = [];
    let accounts = [];
    let currentPage = 1;
    let totalPages = 1;
    // let toggleSetupAccount = false;

    // async function loadInvestmentTransactions(page = 1) {
    //     try {
    //         const params = new URLSearchParams({
    //             skip: (page - 1) * $investmentStore.pagination.itemsPerPage,
    //             limit: $investmentStore.pagination.itemsPerPage
    //         });

    //         const url = `${API_BASE_URL}/stock/investments/transactions?${params}`;
    //         const response = await fetch(url);
            
    //         if (!response.ok) {
    //             throw new Error('Failed to load transactions');
    //         }

    //         const data = await response.json();
    //         console.log('loadInvestmentTransactions:', data);
    //         // store 업데이트
    //         // investmentStore.setTransactions(data);
    //         // investmentStore.setPage(page);
    //         investmentStore.setTransactions(data.items);
    //         investmentStore.setTotalItems(data.pagination.totalItems);
    //         investmentStore.setPage(data.pagination.currentPage);
            
    //     } catch (e) {
    //         console.error('Error loading transactions:', e);
    //     }
    // }

    // function handleTransactionCreated(event) {
    //     loadInvestmentTransactions($investmentStore.pagination.currentPage);
    // }

    function handlePageChange(event) {
        loadInvestmentTransactions(event.detail);
    }

    async function handleAssetAdded(event) {
        event.preventDefault();
        
        try {
            const response = await fetch(`${API_BASE_URL}/stock/investments/assets`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name,
                    code,
                    type,
                    currency,
                    asset_metadata
                })
            });

            if (!response.ok) {
                throw new Error('자산 추가 실패');
            }

            const result = await response.json();
            dispatch('assetAdded', result);
            
            // 입력 폼 초기화
            name = '';
            code = '';
            type = 'STOCK';
            currency = 'KRW';
            asset_metadata = {};
            
        } catch (error) {
            console.error('Error adding asset:', error);
            alert(error.message);
        }
    }

    // async function loadAssets() {
    //     try {
    //         const response = await fetch(API_BASE_URL + '/stock/investments/assets');
    //         if (!response.ok) throw new Error('자산 목록 로드 실패');
    //         const data = await response.json();
    //         investmentStore.setAssets(data);
    //     } catch (error) {
    //         console.error('Error loading assets:', error);
    //     }
    // }

    // async function loadAccounts() {
    //     try {
    //         const response = await fetch(API_BASE_URL + '/stock/investments/accounts');
    //         accounts = await response.json();
    //     } catch (error) {
    //         console.error('Error loading accounts:', error);
    //     }
    // }

    // function handleTransactionCreated(event) {
    //     loadInvestmentTransactions(currentPage);
    // }

    // function handlePageChange(event) {
    //     loadInvestmentTransactions(event.detail);
    // }

    // 초기 데이터 로드
    // loadInvestmentTransactions();
    // loadAssets();
    // loadAccounts();
    // async function loadAssets() {
    //     try {
    //         const response = await fetch(API_BASE_URL + '/stock/investments/assets');
    //         const data = await response.json();
    //         investmentStore.setAssets(data);
    //     } catch (error) {
    //         console.error('Error loading assets:', error);
    //     }
    // }

    function handleAccountsInitialized(event) {
        const newAccounts = event.detail;
        accounts = [...accounts, ...newAccounts];
        console.log('초기화된 계정:', newAccounts);
    }

    function handleAccountAdded(event) {
        const newAccount = event.detail;
        accounts = [...accounts, newAccount];
        console.log('추가된 계정:', newAccount);
    }
    function handleAssetInitialized(event) {
        loadAssets();  // 자산 목록 새로고침
    }

//     let togglesInvestment = [];
//     async function handleInvestmentButton(event) {
//     let type = event.detail;
//     if (togglesInvestment.includes(type)) {
//         togglesInvestment = togglesInvestment.filter(t => t !== type);
//     } else {
//         // 데이터 로딩이 필요한 경우 먼저 처리
//         try {
//             if (type === 'asset_list') {
//                 await loadAssets(); // 데이터 로딩 완료까지 대기
//             } else if (type === 'account_list') {
//                 await loadAccounts(); // 데이터 로딩 완료까지 대기
//             }
//             // 데이터 로딩이 성공한 후에만 토글 추가
//             togglesInvestment = [...togglesInvestment, type];
//         } catch (error) {
//             console.error('데이터 로딩 실패:', error);
//             alert('데이터를 불러오는데 실패했습니다.');
//             return; // 실패시 토글 추가하지 않음
//         }
//     }
//     console.log('토글 상태:', togglesInvestment);
// }


    // 재무제표 데이터 로드
    let quarterBalance = {};
    let toggleQuarterChart = [];
    // 차트 토글 함수
    function doToggleQuarterChart(code) {
        console.log('Toggling chart for code:', code);
        if (toggleQuarterChart.includes(code)) {
            toggleQuarterChart = toggleQuarterChart.filter(c => c !== code);
        } else {
            toggleQuarterChart = [...toggleQuarterChart, code];
        }
        if (toggleQuarterChart.includes(code)) {
            getQuarterBalanceSheet(code);
        }
        console.log('Updated toggleQuarterChart:', toggleQuarterChart);
    }
    // function getQuarterBalanceSheet(symbol) {
    //     const url = '/stock/dart/balance-sheet'
    //     const params = {
    //         key: $key,
    //         symbol: symbol,
    //     }
    //     fastapi('get', url, params, (json) => {
    //         console.log('json:', json);
    //         // 스토어 업데이트
    //         // $investInfoMap[symbol].quarter = json.quarter;
            
    //         // console.log('저장된 데이터:', $investmentStore);

    //         let _quarter = [];
    //         for (let item of Object.values(json.quarter)) {
    //             if (item[0] && item[0].toString().startsWith('20')) {
    //                 let dateStr = item[0].toString();
    //                 let year = dateStr.slice(0, 4);
    //                 let month = dateStr.slice(4, 6);
    //                 let day = dateStr.slice(6, 8);
                    
    //                 // 기본 날짜 형식
    //                 let formattedDate = `${year}-${month}-${day}`;
                    
    //                 // 날짜 중복 확인 및 처리
    //                 while (_quarter.some(q => q.time === formattedDate)) {
    //                     let date = new Date(year, month - 1, day);
    //                     date.setDate(date.getDate() + 7);
                        
    //                     year = date.getFullYear();
    //                     month = String(date.getMonth() + 1).padStart(2, '0');
    //                     day = String(date.getDate()).padStart(2, '0');
    //                     formattedDate = `${year}-${month}-${day}`;
    //                 }

    //                 let value = stringToNumber(item[10].toString())/100000000;
    //                 _quarter.push({
    //                     time: formattedDate,
    //                     value: value, 
    //                     color: 'rgba(128, 128, 128, 0.5)'
    //                 });
    //             }
    //         }

    //         // 시간순으로 정렬
    //         _quarter.sort((a, b) => {
    //             const timeA = new Date(a.time).getTime();
    //             const timeB = new Date(b.time).getTime();
    //             return timeA - timeB;
    //         });

    //         quarterBalance[symbol] = _quarter;

    //         // quarterBalance[symbol] = _quarter;
    //         console.log('quarterBalance:', quarterBalance);
    //         if (!toggleQuarterChart.includes(symbol)) {
    //             toggleQuarterChart.push(symbol);
    //         } else {
    //             toggleQuarterChart = toggleQuarterChart.filter(s => s !== symbol);
    //         }
    //     });
    // }


    // 컴포넌트 언마운트 시 연결 종료
    onDestroy(async () => {
        closeAllConnections();   // WebSocket 연결 종료
    
        charts.forEach(chart => chart.remove());
        charts.clear();
        candleSeriesMap.clear();
        volumeSeriesMap.clear();
        chartContainers.clear();
        additionalSeriesMap.clear();
        // $investmentStore.resetAllPagination();


        isLoading = false;
    });




</script>

<div class="stock-container">

    <!-- 거래 로그 입력 폼 -->
    {#if isTradeLog}
    <div class="setup-trade-log-container">
        
        <!-- 입력 폼 -->
        <div class="trade-log-input-form">
                
                <!-- 추가, 수정 편집 버튼 -->
            <div class="input-row" style = "padding-bottom: 20px;">
                    {#if !isEditTrade}
                <button 
                    class="add-trade-button"
                    on:click={addTrade}
                >
                    추가
                        </button>
                    {/if}
                    {#if isEditTrade}
                        <button 
                            class="add-trade-button update-color"
                            on:click={() => updateTrade(trade_id)}
                        >
                            수정
                        </button>
                    {/if}
                    
                    <button 
                        class="add-trade-button"
                        class:edit-trade={isEditTrade}
                        on:click={toggleEditTrade}
                    >
                        편집
                </button>
                <input 
                    type="date" 
                    bind:value={date}
                        autocomplete="off"
                        autocorrect="off"
                        autocapitalize="off"
                        spellcheck="false"
                    class="trade-input date-input"
                />
                    <!-- 자산 입력 폼 선택 select -->
                    {#if !isEditTrade}
                <select 
                    bind:value={assetCategory}
                    class="category-select trade-input"
                    on:change={() => resetTradeLog()}
                >
                    <option value="">구분 선택</option>
                    {#each assetCategories as category}
                        <option value={category.value}>{category.label}</option>
                    {/each}
                </select>
                    {/if}

                    <!-- 주식, 가상화폐, 환전 거래 radio 버튼 -->
                    {#if !assetCategory.includes('cash')}    
                    <div class="radio-group">
                        <label class="radio-label">
                            <input 
                                type="radio" 
                                bind:group={action} 
                                value="in"
                                class="trade radio-input"
                            />
                            <span class="radio-text">Buy</span>
                        </label>

                        <label class="radio-label">
                            <input 
                                type="radio" 
                                bind:group={action} 
                                value="out"
                                class="trade radio-input"
                            />
                            <span class="radio-text">Sell</span>
                        </label>
                    </div>
                {/if}

                    <!-- 현금 radio 버튼 -->
                    {#if assetCategory.includes('cash')}
                    <div class="radio-group">
                        <label class="radio-label">
                            <input 
                                type="radio" 
                                bind:group={action} 
                                    on:change={() => {assetCategory = 'cash.deposit';}}
                                value="in"
                                class="trade radio-input"
                            />
                                <span class="radio-text">입금</span>
                        </label>
                        <label class="radio-label">
                            <input 
                                type="radio" 
                                bind:group={action} 
                                    on:change={() => {assetCategory = 'cash.withdrawal';}}
                                value="out"
                                class="trade radio-input"
                            />
                                <span class="radio-text">출금</span>
                        </label>
                    </div>
                {/if}
            </div>
                <!-- 자산 정보 표시 -->
                <div class="input-row">
                    <span class="amount-korean">{assetCategory.replace(',', '  ')}</span>
                </div>
            
            <!-- 주식, 가상화폐 거래 입력 폼 -->
                {#if !assetCategory.includes('exchange') && !assetCategory.includes('cash') && !action == ''}
                <div class="stock input-row">
                    <input 
                        type="text" 
                        bind:value={assetCategory}
                        placeholder="구분"
                        class="trade-input category-input gubun-input"
                    />
                        <select 
                            class="trade-input gubun-input"
                            bind:value={assetCategory}
                           
                            tabindex="0"
                        >   <option value="">자산선택</option>
                            {#each Object.keys(trade_tag.asset_categories_obj) as _asset_category}

                                    <option value={_asset_category}>{_asset_category}</option>

                            {/each}
                        </select>
                        <select 
                            class="trade-input gubun-input"
                            
                            on:change={(e) => {
                                selectAssetCategory(e.target.value);
                                e.target.value = '';
                            }}
                            tabindex="0"
                        >
                            <option value="">구분</option>
                            {#each trade_tag.asset_categories_obj[(assetCategory+',').split(',')[0]].sub as _asset_category}
                                <option value={_asset_category}>{_asset_category}</option>
                    {/each}
                        </select>
                        <select 
                            class="trade-input gubun-input"
                            on:change={(e) => {
                                selectCurrency(e.target.value);
                                e.target.value = '';
                            }}
                            tabindex="0"
                        >   
                            <option value="">통화</option>
                            {#each trade_tag.currencies as _currency}
                                <option value={_currency}>{_currency}</option>
                            {/each}
                        </select>
                </div>
                <div class="input-row">
                    <input 
                        type="text" 
                        bind:value={market}
                        placeholder="시장구분"
                        class="trade-input gubun-input"
                    />
                        <select 
                            class="tag-button "
                            bind:value={market}
                            tabindex="0"
                        >
                            {#each trade_tag.trade_market as _market}
                                <option value={_market}>{_market}</option>
                    {/each}
                        </select>
                </div>


                <!-- 종목명 검색 입력 폼 -->
                    <div class="input-row search-container">
                    <div class="search-container">
                        <input 
                            type="text" 
                            bind:value={name}
                            placeholder="종목명"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                            
                            class="trade-input gubun-input stock-input"
                            on:input={handleSearchInput}
                            on:keydown={tradeSearch}
                        />
                            <!-- 자동 검색 -->
                        {#if searchResults.length > 0}
                            <div class="search-results" transition:slide>
                                {#each searchResults as result, index}
                                    <button 
                                        class="search-result-item"
                                        class:selected={index === selectedIndex}
                                        on:click={() => {
                                                // assetCategory = 'stock.krw'
                                                selectCurrency('krw', true);
                                            code = result.shcode; 
                                            name = result.shname;
                                            searchResults = [];
                                            selectedIndex = -1;
                                            if (result.gubun === '1') {
                                                market = 'KOSPI';
                                            } else if (result.gubun === '2') {
                                                market = 'KOSDAQ';
                                            }
                                        }}
                                        on:mouseenter={() => selectedIndex = index}
                                    >
                                        <span class="result-code">{result.shcode}</span>
                                        <span class="result-name">{result.shname}</span>
                                    </button>
                                {/each}
                            </div>
                        {/if}
                    </div>
                        <div class="trade-name-container">
                            <select 
                                class="trade-input gubun-input"
                                bind:value={name}
                                on:change={(e) => {
                                    code = name.code;
                                    market = name.market;
                                    name = name.name;
                                    const isEnglish = /^[A-Za-z]+$/.test(code); 
                                    if (isEnglish) {
                                        // console.log('code:', code);
                                        selectCurrency('usd', true);
                                    } else {
                                        selectCurrency('krw', true);
                                    }
                                }}
                            >
                                <option value="">보유종목 선택</option>
                                {#each trade_tag.trade_name as _stock}
                                    {#if _stock.asset_category.includes('stock')}
                                        <option value={_stock}>{_stock.name}</option>
                                    {/if}
                    {/each}
                            </select>
                        
                        </div>
                    {#if _stocks.length > 0}
                        <select 
                            class="trade-input gubun-input"
                            on:change={(e) => {
                                const stock = _stocks.find(s => s.한글기업명 === e.target.value);
                                if (stock) {
                                    name = stock.한글기업명;
                                    code = stock.종목코드;
                                    market = stock.시장구분 === '1' ? 'KOSPI' : 'KOSDAQ';
                                }
                            }}
                        >
                            <option value="">종목 선택</option>
                            {#each _stocks as stock}
                                <option value={stock.한글기업명}>
                                    {stock.한글기업명}
                                </option>
                            {/each}
                        </select>
                    {/if}

                </div>

                    <!-- 종목코드 입력 폼 -->
                <div class="input-row">
                    <input 
                        type="text" 
                        bind:value={code}
                        placeholder="종목코드"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="trade-input gubun-input"
                    />
                    
                </div>
                
                    <!-- 수량 입력 폼 -->
                    {#if !assetCategory.includes('dividend')}
                <div class="input-row">
                    <input 
                        type="number" 
                        bind:value={quantity}
                        placeholder="수량"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                        class="quantity trade-input"
                        class:trade-blue={action === 'out'}
                        class:trade-red={action === 'in'}
                                readonly={!isEditTrade}
                            />
                            <input 
                                type="number" 
                                bind:value={quantity0}
                                placeholder="수량1"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="quantity trade-input"
                                class:trade-blue={action === 'out'}
                                class:trade-red={action === 'in'}
                            />
                            <input 
                                type="number" 
                                bind:value={quantity1}
                                placeholder="수량2"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="quantity trade-input"
                                class:trade-blue={action === 'out'}
                                class:trade-red={action === 'in'}
                            />
                            <input 
                                type="number" 
                                bind:value={quantity2}
                                placeholder="수량3"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="quantity trade-input"
                                class:trade-blue={action === 'out'}
                                class:trade-red={action === 'in'}
                            />
                </div>

                        <!-- 가격 입력 폼 -->
                <div class="input-row">
                    <input 
                        type="number" 
                        bind:value={price}
                        placeholder="가격"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                        class="price trade-input"
                                readonly={!isEditTrade}
                            />
                            <input 
                                type="number" 
                                bind:value={price0}
                                placeholder="가격1"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="price trade-input"
                            />
                            <input 
                                type="number" 
                                bind:value={price1}
                                placeholder="가격2"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="price trade-input"
                            />
                            <input 
                                type="number" 
                                bind:value={price2}
                                placeholder="가격3"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="price trade-input"
                            />
                </div>
                        
                    {/if}
                    <!-- 금액 입력 폼 -->
                <div class="input-row">
                    <input 
                        type="number" 
                        bind:value={amount}
                        placeholder="금액"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="amount trade-input"
                        class:trade-red={action === 'out'}
                        class:trade-blue={action === 'in'}
                            readonly={!assetCategory.includes('dividend') || !isEditTrade}
                    />
                            <!-- readonly -->
                    <span class="amount-korean">{formatNumber(amount)}원</span>
                </div>
                  
                    
                    <!-- 수수료, 세금 입력 폼 -->
                        <div class="input-row">
                            <input 
                                type="number" 
                                bind:value={fee}
                                placeholder="수수료"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="amount trade-input"
                                readonly
                            />
                            <span class="amount-korean">{formatNumber(fee)}원</span>
                        </div>
                        <div class="input-row">
                            <input 
                                type="number" 
                                bind:value={tax}
                                placeholder="세금"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="amount trade-input"
                                readonly
                            />
                            <span class="amount-korean">{formatNumber(tax)}원</span>
                        </div>

            {/if}
            <!-- 환전 거래 입력 폼 -->
                {#if assetCategory.includes('exchange') && !action == ''}
                <div class="stock input-row">
                    <input 
                    type="text" 
                    bind:value={assetCategory}     
                    placeholder="구분"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                    class="trade-input gubun-input"
                    />
                        <select 
                            class="trade-input gubun-input"
                            bind:value={assetCategory}
                        
                            tabindex="0"
                        >   <option value="">자산선택</option>
                            {#each Object.keys(trade_tag.asset_categories_obj) as _asset_category}

                                    <option value={_asset_category}>{_asset_category}</option>

                            {/each}
                        </select>
                        
                        <select 
                            class="trade-input gubun-input"
                            on:change={(e) => {
                                selectCurrency(e.target.value);
                                e.target.value = '';
                            }}
                            tabindex="0"
                        >   
                            <option value="">통화</option>
                            {#each trade_tag.currencies as _currency}
                                <option value={_currency}>{_currency}</option>
                            {/each}
                        </select>
                </div>
                <div class="input-row">
                    <!-- 환전할 통화 -->
                    <input 
                        type="text" 
                        bind:value={name}
                        placeholder="외화 USD"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="trade-input gubun-input"
                    />
                    {#each trade_tag.exchange_name as exchange}
                        <button 
                            class="tag-button badge"
                            on:click={() => {name = exchange}}
                            tabindex="0"
                        >
                            {exchange}
                        </button>
                    {/each}
                </div>
                <div class="input-row">
                    <!-- 환전받을 통화 -->
                    <input 
                        type="text" 
                        bind:value={code}
                        placeholder="원화 KRW"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="trade-input gubun-input"
                    />
                    {#each trade_tag.exchange_code as exchange}
                        <button 
                            class="tag-button badge"
                            on:click={() => {code = exchange}}
                            tabindex="0"
                        >
                            {exchange}
                        </button>
                    {/each}
                </div>
                
                <div class="input-row">
                    <!-- 환전할 금액 -->
                    <input 
                        type="number" 
                        bind:value={quantity}
                        placeholder="외화금액 USD"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="exchange trade-input"
                        class:trade-blue={action === 'out'}
                        class:trade-red={action === 'in'}
                    />
                        <span class="amount-korean">{formatNumber(quantity)} {name}</span>
                </div>
                <div class="input-row">
                    <!-- 환율 -->
                    <input 
                        type="number" 
                        bind:value={price}
                        placeholder="환율"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="exchange trade-input"
                    />
                    <span class="amount-korean">{formatNumber(price)}원</span>
                </div>
                <div class="input-row">
                    <!-- 환전받을 금액 -->
                    <input 
                        type="number" 
                        bind:value={amount}
                        placeholder="원화금액 KRW"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="exchange trade-input"
                        class:trade-red={action === 'out'}
                        class:trade-blue={action === 'in'}
                    />
                            <!-- readonly -->
                        <span class="amount-korean">{formatNumber(amount)} {code}</span>
                </div>
            {/if}

                <!-- 현금 입출금 입력 폼 -->
                {#if assetCategory.includes('cash') && !action == ''}
                <div class="input-row">
                    <input 
                        type="text" 
                        bind:value={assetCategory}
                        placeholder="구분"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="trade-input gubun-input"
                    />
                        <select 
                            class="trade-input gubun-input"
                            bind:value={assetCategory}
                        
                            tabindex="0"
                        >   <option value="">자산선택</option>
                        {#each Object.keys(trade_tag.asset_categories_obj) as _asset_category}

                                <option value={_asset_category}>{_asset_category}</option>

                        {/each}
                    </select>
                    <select 
                        class="trade-input gubun-input"
                        
                        on:change={(e) => {
                            selectAssetCategory(e.target.value);
                            e.target.value = '';
                        }}
                        tabindex="0"
                    >   
                        <option value="">입출금</option>
                        {#each trade_tag.asset_categories_obj[(assetCategory+',').split(',')[0]].sub as _asset_category}
                            <option value={_asset_category}>{_asset_category}</option>
                        {/each}
                    </select>
                    <select 
                        class="trade-input gubun-input"
                        on:change={(e) => {
                            selectCurrency(e.target.value);
                            e.target.value = '';
                        }}
                        tabindex="0"
                    >   
                        <option value="">통화</option>
                        {#each trade_tag.currencies as _currency}
                            <option value={_currency}>{_currency}</option>
                        {/each}
                    </select>
                </div>
                <div class="input-row">
                    <input 
                        type="text" 
                        bind:value={code}
                            placeholder="계좌"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="trade-input gubun-input"
                    />
                    </div>
                    <div class="input-row">
                        <input 
                            type="text" 
                            bind:value={name}
                            placeholder="계좌명"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                            class="trade-input gubun-input"
                        />
                        <!-- 통화 선택 -->
                        <select 
                            bind:value={code}
                            on:change={() => {
                                assetCategory = code.asset_category
                                name = code.name
                                code = code.code
                            }}
                            class="trade-input gubun-input"
                        >
                            {#each trade_tag.cashes as cash}
                                <!-- {#if cash.includes('cash')} -->
                                    <option value={cash}>
                                        {cash.name}
                                    </option>
                                <!-- {/if} -->
                    {/each}
                        </select>
                </div>
                <div class="input-row">
                    <input 
                        type="number" 
                        bind:value={amount}
                        placeholder="금액"
                            autocomplete="off"
                            autocorrect="off"
                            autocapitalize="off"
                            spellcheck="false"
                        class="trade-input gubun-input"
                        class:trade-red={action === 'in'}
                        class:trade-blue={action === 'out'}
                    />
                    <span class="amount-korean">{formatNumber(amount)}원</span>
                    <span class="amount-korean">{numberToKorean(amount)}원</span>
                    </div>
                    <!-- 수수료, 세금 입력 폼 -->
                        <div class="input-row">
                            <input 
                                type="number" 
                                bind:value={fee}
                                placeholder="수수료"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="amount trade-input"
                                readonly
                            />
                            <span class="amount-korean">{formatNumber(fee)}원</span>
                        </div>
                        <div class="input-row">
                            <input 
                                type="number" 
                                bind:value={tax}
                                placeholder="세금"
                                autocomplete="off"
                                autocorrect="off"
                                autocapitalize="off"
                                spellcheck="false"
                                class="amount trade-input"
                                readonly
                            />
                            <span class="amount-korean">{formatNumber(tax)}원</span>
                </div>
            {/if}
                
                <!-- 메모 입력 폼 -->
            <div class="input-row">
                <input 
                    type="text" 
                    bind:value={memo}
                    placeholder="메모"
                    class="memo trade-input"
                />
            </div>
        </div>
        <!-- 입력 폼 끝 -->


            <!-- 자산 요약 -->
            <AssetSummary asset_summary={trade_tag.asset_summary} />

        <!-- 테이블 -->
         <!-- 선택 버튼 stock, crypto, cash, exchange -->
        <div class="setup-trade-log-table">
            <div class="input-row">
                    {#each Object.keys(trade_tag.asset_categories_obj) as _asset_category}
                        <button 
                    class="tag-button badge add-trade-button"
                            class:active={assetCategory.includes(_asset_category)}
                    on:click={() => {
                                assetCategory = _asset_category;
                                code = '';
                                startDate = '';
                                endDate = '';
                                $trade_keyword = {};
                                fetchTrades()
                            }}
                            tabindex="0"
                        >
                            {_asset_category}
                        </button>
                    {/each}
                </div>
                {#if trade_tag.asset_categories_obj[(assetCategory + ',').split(',')[0]]}
                    <div class="input-row">
                        {#each trade_tag.asset_categories_obj[(assetCategory + ',').split(',')[0]].sub as _asset_category}
                            <button 
                                class="tag-button badge add-trade-button"
                                class:active={assetCategory.includes(_asset_category)}
                                on:click={() => {
                                    selectAssetCategory(_asset_category);
                                    // assetCategory = _asset_category;
                                    // code = '';
                        // startDate = '';
                        // endDate = '';
                                    // $trade_keyword = {};
                        // fetchTrades()
                    }}
                    tabindex="0"
                >
                                {_asset_category}
                            </button>
                            {/each}
                            {#each trade_tag.asset_categories_obj[(assetCategory + ',').split(',')[0]].currency as _asset_category}
                    <button 
                        class="tag-button badge add-trade-button"
                                    class:active={assetCategory.includes(_asset_category)}
                        on:click={() => {
                                        selectCurrency(_asset_category);
                                        // assetCategory = _asset_category;
                                        // code = '';
                                        // startDate = '';
                                        // endDate = '';
                                        // $trade_keyword = {};
                                        // fetchTrades()
                        }}
                        tabindex="0"
                    >
                        {_asset_category}
                    </button>
                {/each}
            </div>
                {/if}


            <!-- 테이블 시작 -->
            <div class="setup-trade-log-table">
                    <!-- 주식, 가상화폐, 기타 -->
                    {#if !assetCategory.includes('exchange') && !assetCategory.includes('cash') && assetCategory != ''}
                    <p class="trade-log-table-title">주식, 가상화폐, 기타</p>
                        <div class="table-container">
                    <table class="trade-log-table">
                        <thead>
                            <tr>
                                        <th class="text-right trade-log-table date">날짜</th>
                                        <!-- <th class="text-right">구분</th> -->
                                        <!-- <th class="text-right trade-log-table market">시장구분</th> -->
                                        <th class="text-right trade-log-table name">종목명</th>
                                        <th class="text-right trade-log-table holdings_quantity">보유</th>
                                        <th class="text-right trade-log-table purchases_price">평균단가</th>
                                        <th class="text-right trade-log-table quantity">수량</th>
                                        <th class="text-right trade-log-table price">가격</th>
                                        <th class="text-right trade-log-table amount">금액</th>
                                        <!-- <th class="text-right trade-log-table balance">잔고</th> -->
                                        <th class="text-right trade-log-table fee">fee</th>
                                        <th class="text-right trade-log-table tax">tax</th>
                            </tr>
                        </thead>
                                
                        <tbody>
                            {#each trades as trade}
                                <tr>
                                            <td class="text-right trade-log-table date" class:text-blue={trade.quantity < 0}>
                                                {#if isEditTrade}
                                        <button 
                                            class="delete-badge"
                                            on:click={() => deleteTrade(trade.id)}
                                        >
                                            ×
                                        </button>
                                                <button 
                                                    class="edit-badge"
                                                    on:click={() => tradeEdit(trade.id)}
                                                >
                                                    ✎
                                                </button>
                                                {/if}
                                                {trade.date.slice(5, 10)}
                                    </td>
                                            <!-- <td class="text-right trade-log-table market" class:text-blue={trade.quantity < 0}>{trade.asset_category.replace('stock,', '')}</td> -->
                                            <!-- <td class="text-right"
                                                class:text-bluet={trade.quantity < 0}
                                            >{trade.market}</td> -->
                                            <td class="text-right trade-log-table name"class:text-blue={trade.quantity < 0}>
                                                <StockNameButton 
                                                    date={trade.date}
                                                    code={trade.code}
                                                    name={trade.name}
                                                    assetCategory={trade.asset_category}
                                                    bind:trade={trade}
                                                    {searchByCode}
                                                    {selectAssetCategory}
                                                />
                                            </td>
                                            <td class="text-right trade-log-table holdings_quantity" class:text-blue={trade.quantity < 0}>{formatNumber(trade.holdings_quantity)}</td>
                                            <td class="text-right trade-log-table holdings_quantity" class:text-blue={trade.quantity < 0}>{formatNumber(trade.purchases_price)}</td>
                                            <td class="text-right trade-log-table quantity" class:text-blue={trade.quantity < 0}>{formatNumber(trade.quantity)}</td>
                                            <td class="text-right trade-log-table price" class:text-blue={trade.quantity < 0}>{formatNumber(trade.price)}</td>
                                            <td class="text-right trade-log-table amount" class:text-blue={trade.quantity < 0}>{formatNumber(trade.amount)}</td>
                                            <!-- <td class="text-right trade-log-table balance" class:text-blue={trade.quantity < 0}>{formatNumber(trade.balance)}</td> -->
                                            <td class="text-right trade-log-table fee" class:text-blue={trade.quantity < 0}>{formatNumber(trade.fee)}</td>
                                            <td class="text-right trade-log-table tax" class:text-blue={trade.quantity < 0}>{formatNumber(trade.tax)}</td>
                                </tr>
                                        {#if trade.showDetails && trade.taxData}
                                        <tr class="detail-row">
                                            <td colspan="9">
                                                <div class="detail-content">
                                                    {#if trade.taxData.capital_gains?.length > 0}
                                                        {#each trade.taxData.capital_gains as gain}
                                                            <TaxDetailRow {gain} />
                                                        {/each}
                                                    {:else}
                                                        <div class="no-data">양도소득 내역이 없습니다.</div>
                                                    {/if}
                                                </div>
                                            </td>
                                        </tr>
                                        {/if}
                            {/each}
                        </tbody>
                    </table>
                        </div>
                {/if}

                    <!-- 환전, 통화 -->
                    {#if assetCategory.includes('exchange')}
                    <p class="trade-log-table-title">환전, 통화</p>
                    <table class="trade-log-table">
                        <thead>
                            <tr>
                                    <th class="text-right">날짜</th>
                                    <th class="text-right">통화</th>
                                    <th class="text-right">원화</th>
                                    <th class="text-right">외화</th>
                                    <th class="text-right">환율</th>
                                    <th class="text-right">금액</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each trades as trade}
                                <tr>
                                        <td class="trade-date-cell text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >
                                            {#if isEditTrade}
                                        <button 
                                                class="delete-badge text-right"
                                            on:click={() => deleteTrade(trade.id)}
                                        >
                                            ×
                                        </button>
                                            {trade.id}
                                            <button 
                                                class="edit-badge"
                                                on:click={() => tradeEdit(trade.id)}
                                            >
                                                ✎
                                            </button>
                                            {/if}
                                        {trade.date}
                                    </td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{trade.name}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{trade.code}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.quantity)}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.price)}</td>
                                        <td class="text-right"
                                            class:text-blue={trade.quantity < 0}
                                        >{formatNumber(trade.amount)}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {/if}

                    <!-- 현금 -->
                    {#if assetCategory.includes('cash')}
                        <p class="trade-log-table-title">현금</p>
                    <table class="trade-log-table">
                        <thead>
                            <tr>
                                    <th class="text-right">날짜</th>
                                    <th class="text-right">시장구분</th>
                                    <th class="text-right">계좌</th>
                                    <th class="text-right">계좌명</th>
                                    <th class="text-right">금액</th>
                                    <th class="text-right">fee</th>
                                    <th class="text-right">tax</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each trades as trade}
                                <tr>
                                        <td class="trade-date-cell text-right">
                                            {#if isEditTrade}
                                        <button 
                                            class="delete-badge"
                                            on:click={() => deleteTrade(trade.id)}
                                        >
                                            ×
                                        </button>
                                                <button 
                                                    class="edit-badge"
                                                    on:click={() => tradeEdit(trade.id)}
                                                >
                                                    ✎
                                                </button>
                                            {/if}
                                        {trade.date}
                                    </td>
                                        <td class="text-right">{trade.asset_category}</td>
                                        <td class="text-right">{trade.code}</td>
                                        <td class="text-right">{trade.name}</td>
                                        <td class="text-right">{formatNumber(trade.amount)}</td>
                                        <td class="text-right">{formatNumber(trade.fee)}</td>
                                        <td class="text-right">{formatNumber(trade.tax)}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {/if}

                    <!-- 페이지네이션 -->
                <div class="pagination-container">
                    <Pagination 
                        {currentPage}
                        {totalPages}
                        on:pageChange={(e) => {
                                currentPage = e.detail;
                                fetchTrades();  // 여기서 데이터 조회
                        }}  
                    />
                </div>
            </div>
        </div>
    </div>
{/if}




    <!-- investment 페이지 -->
    <div class="investment-page">
        {#if browser && $investmentStore.toggles.includes('transactionslist')}
            <TransactionsList />
        {/if}
        {#if browser && $investmentStore.toggles.includes('transactionForm')}
            <TransactionForm />
        {/if}
        {#if browser && $investmentStore.toggles.includes('transactionSummary')}
            <TransactionSummary />
        {/if}
        {#if browser && $investmentStore.toggles.includes('transaction_list')}
            <TransactionList />
            {/if}
        </div>

    <div class="investment-page">
        {#if browser && $investmentStore.toggles.includes('asset_add')}
            <AssetForm />
            {/if}
        {#if browser && $investmentStore.toggles.includes('asset_init')}
            <AssetInitialize />
                {/if}
        {#if browser && $investmentStore.toggles.includes('asset_list')}
            <AssetList />
                {/if}
        </div>
    <div class="accounts-page">
        {#if browser && $investmentStore.toggles.includes('account_add')}
            <AccountForm />
        {/if}
        {#if browser && $investmentStore.toggles.includes('account_init')}
            <AccountInitialize />
        {/if}
        {#if browser && $investmentStore.toggles.includes('account_list')}
            <AccountList />
        {/if}
    </div>

 
    
    <!-- 투자 버튼 -->
    <InvestmentButton/>



    <!-- 환율 정보 입력 -->
    <ExchangeRateForm />


    <!-- 주기적 투자 수익 계산 -->
    <TransactionPeriodicReturn />
    
    <!-- 투자 수익 계산 -->
    <TransactionReturn />
    

    
    <div class="accno-container">
        <KeyInputForm
        {isSetupKey}
            {isLoading}
            bind:cname
            bind:appkey
            bind:appsecretkey
            bind:key={$key}
            {clearKey}
            {setupLsOpenApiDb}
            {fetchAccnoList}
            {toggleTradeLog}
            {isTradeLog}
            bind:trade_tag={trade_tag}
            />
            
            
            <AccountTable 
            accnoCodes={accnoCodes}
            accno_list={$accno_list}
            asset_summary={trade_tag.asset_summary}
            trade_tag={trade_tag}
        />
    </div>
    
    




    <!-- 키 입력 폼 -->
<!-- 관심종목 추가 -->
<div class="interest-container">
    
    <!-- 테이블 상단 버튼 그룹 -->
    {#if !showInterestInput}
        <div class="button-group">
            <button 
                class="toggle-button"
                on:click={toggleInterestInput}
            >
                추가 +
            </button>
            <button 
                class="load-button"
                class:loading={loadingMultiInvestInfo}
                on:click={getMultiInvestInfo}
                disabled={loadingMultiInvestInfo}
            >
                {#if loadingMultiInvestInfo}
                    ...
                {:else}
                    정보
                {/if}
            </button>
            <button 
                class="load-button"
                class:loading={loadingInterestStocks}   
                on:click={getInterestStocks}
                disabled={loadingInterestStocks}
            >   
                {#if loadingInterestStocks}
                    조회중...
                {:else}
                    주가
                {/if}
            </button>
            {#if !isSelectMode}
                <button 
                    class="load-button"
                    on:click={toggleSelectMode}
                    >
                    삭제
                </button>
            {:else}    
                <button 
                    class="load-button delete-button"
                    on:click={toggleSelectMode}
                    >
                    삭제
                </button>
            {/if}
            {#if !isTest}
                <button 
                    class="load-button"
                    on:click={toggleTest}
                >
                    테스트
                </button>
            {:else}
                <button 
                    class="load-button delete-button"
                    on:click={toggleTest}
                >
                    테스트
                </button>
            {/if}
            {#if !isDirectWss}
                <button 
                    class="load-button"
                    on:click={directWss}
                >
                    Wss연결
                </button>
            {:else}
                <button 
                    class="load-button delete-button"
                    on:click={() => closeDirectWss('direct')}
                >
                    Wss종료
                </button>
            {/if}
            {#if view_selected_stocks}
                <button 
                    class="load-button delete-button"
                    on:click={toggleSelectedStocks}
                >
                    정보
                </button>
            {:else}
                <button 
                    class="load-button"
                    on:click={toggleSelectedStocks}
                >
                    정보
                </button>
            {/if}
            
            {#if view_selected_stock}
                <button 
                    class="load-button delete-button"
                    on:click={toggleViewSelectedStock}
                >
                    종목선택
                </button>
            {:else}
                <button 
                    class="load-button"
                    on:click={toggleViewSelectedStock}
                >
                종목선택
                </button>
            {/if}
        </div>

        <div class="button-group sub-button-group">
            {#if stock && view_selected_stock}
                <div class="button-row">
                    <span class="stock-tag-name text-gradient">{stock?.db?.한글기업명}</span>
                    {#if !showChart}
                    <input 
                        class="input-group text tag stock-tag"
                        type="text" 
                        value={tag || ''} 
                        on:input={(e) => tag = e.target.value}
                            maxlength="7"  
                            placeholder={stock?.db?.tag || ''}  
                        />
                        
                        <button 
                        class="load-button"
                        on:click={addInterestStockTag}
                        >
                        태그입력
                    </button>
                    {/if}
                    <button 
                    class="load-button"
                        on:click={getInvestInfoStock}
                    >
                        정보받기
                    </button>
                    <button 
                        class="load-button"
                        on:click={viewInvestInfoStock}
                        >
                        정보보기
                    </button>
                    {#if showChart && stock}
                            <div class="input-group chart-controls">
                                <input
                                    class="input-group input-count"
                                    type="number" 
                                    bind:value={qrycnt}
                                    min="1"
                                    max="250"
                                    placeholder="100"
                                />
                                <select 
                                    class="select-period"
                                    bind:value={chartPeriod}
                                    on:change={() => updateChartPeriod(stock.db.종목코드, true)} 
                                >
                                    <option value="2">일봉</option>
                                    <option value="3">주봉</option>
                                    <option value="4">월봉</option>
                                </select>
                            </div>


                        <button class="load-button delete-button" on:click={toggleChart}>
                            차트
                        </button>
                    {:else}
                        <button class="load-button" on:click={toggleChart}>
                            차트
                        </button>
                    {/if}
                </div>
            {/if}  
        </div>

        <div class="button-group select-button-group">
            {#if isSelectMode}
                <div class="button-row">
                    <span class="selected-count">
                        선택: {codes_select.length}개
                    </span>
                    <button 
                        class="load-button delete-button"
                        on:click={deleteInterestStocks}
                        disabled={codes_select.length === 0}
                    >
                        삭제
                    </button>
                    <button 
                        class="load-button"
                        on:click={toggleSelectMode}
                    >
                            취소
                    </button>
                </div>
            {/if}
        </div>

    {:else}

        <!-- 관심종목 입력 그룹 -->
        <div class="interest-input-group" transition:slide>
            <div class="search-container">
                <input 
                    type="text" 
                    bind:value={newStockCode}
                    placeholder="종목코드 또는 기업명"
                    maxlength="6"
                    class="input-group stock-input"
                    on:input={handleSearchInput}
                    on:keydown={(e) => e.key === 'Enter' && addInterestStock()}
                />
                {#if searchResults && searchResults.length > 0}
                    <div class="search-results" transition:slide>
                        {#each searchResults as result}
                            <button 
                                class="search-result-item"
                                on:click={() => selectSearchResult(result.shcode)}
                            >
                                <span class="result-code">{result.shcode}</span>
                                <span class="result-name">{result.shname}</span>
                            </button>
                        {/each}
                    </div>
                {/if}
            </div>
            <button 
                class="toggle-button"
                on:click={addInterestStock}
                disabled={!newStockCode || newStockCode.length !== 6}
            >
                추가
            </button>
            <button 
                class="load-button"
                on:click={toggleInterestInput}
            >
                취소
            </button>
        </div>
    {/if}

    <!-- 보유종목 목록 -->
    <div class="interest-stock-container">
        {#if $investInfoMap && Object.keys($investInfoMap).length > 0}
            <table class="interest-stock-table">
                <thead class="interest-stock-header">
                    <tr class="stock-header-row">
                        <!-- 선택 모드 헤더 -->
                        {#if isSelectMode}
                            <th class="text-right select-header" on:click={() => {
                                if (codes_select.length > 0) {
                                    codes_select = [];  // 전체 해제
                                } else {
                                    codes_select = Object.keys($investInfoMap);  // 전체 선택
                                }
                                codes_select = [...codes_select];  // 반응성 트리거
                            }}>
                                {codes_select.length > 0 ? '해제' : '선택'}
                            </th>
                        {/if}
                        <th class="text-right"></th>
                        <th class="code-header text-right">
                            <select 
                                bind:value={selectedDetail.field}
                                on:change={() => {
                                    const option = detailOptions.find(opt => opt.value === selectedDetail.field);
                                    selectedDetail.label = option?.label || '';
                                    if (selectedDetail.field) sortStocks(selectedDetail.field);
                                }}
                            >
                                {#each detailOptions as option}
                                    <option value={option.value}>{option.label}</option>
                                {/each}
                            </select>
                        </th>
                        <!-- <th class="text-right">코드</th> -->
                        <!-- <th class="text-right">업종</th> -->
                        <!-- <th class="text-right">메모</th> -->
                        <th class="text-right">종목명</th>
                        <th class="text-right">현재가</th>
                        <th class="text-right">등락률</th>
                        <th class="text-right">거래량</th>
                        <th class="text-right">체결량</th>
                        <th class="text-right"> </th>

                    </tr>
                </thead>
                <tbody>
                    {#each $sortedCodes as code}
                        <tr 
                            class="stock-row" 
                            class:active={view_selected_stocks ? $selectedStocks[code] : false}
                            class:owned-stock={accnoCodes.includes(code)}
                        >
                            <!-- 선택 모드 셀 -->
                            {#if isSelectMode}
                                <td class="select-cell">
                                    <input 
                                        class="input-group"
                                        type="checkbox" 
                                        checked={codes_select.includes(code)}
                                        on:change={(e) => {
                                            e.stopPropagation(); 
                                            toggleStockSelection(code);
                                        }}
                                        on:click={(e) => e.stopPropagation()}  
                                    />
                                </td>
                            {/if}
                            <td class="market-type">{$investInfoMap[code]?.db?.시장구분}</td>
                            <td class="stock-code">
                                {#if selectedDetail.field}
                                    <div class="detail-value-container">
                                        <!-- <span class="detail-label">{selectedDetail.label}:</span> -->
                                        <span class="detail-value">{getDetailValue(code, selectedDetail.field)}</span>
                                    </div>
                                {:else}
                                    {code}
                                {/if}
                            </td>
                            <td 
                                class="stock-name text-gradient text-right"
                                class:active={view_selected_stocks ? $selectedStocks[code] : false}
                                class:owned-stock={accnoCodes.includes(code)}
                                on:click={() => isSelectMode ? toggleStockSelection(code) : handleStockClick(code)}
                            >
                                {$investInfoMap[code]?.db?.한글기업명}
                            </td>
                            {#if $investInfoMap[code]?.t8407OutBlock1}
                                <td class="text-right stock-price"
                                    class:positive={($investInfoMap[code]?.t8407OutBlock1?.등락율 || 0) > 0}
                                    class:negative={($investInfoMap[code]?.t8407OutBlock1?.등락율 || 0) < 0}
                                    on:click={() => doToggleQuarterChart(code)}
                                >{formatNumber($investInfoMap[code]?.t8407OutBlock1?.현재가 || 0)}</td>

                                
                                <td class="text-right stock-ratio"
                                    class:positive={($investInfoMap[code]?.t8407OutBlock1?.등락율 || 0) > 0}
                                    class:negative={($investInfoMap[code]?.t8407OutBlock1?.등락율 || 0) < 0}
                                >{$investInfoMap[code]?.t8407OutBlock1?.등락율 || 0}</td>
                                <td class="text-right stock-volume">
                                    {formatNumber($investInfoMap[code]?.t8407OutBlock1?.누적거래량 || 0)}
                                </td>
                                <td class="text-right stock-cvolume"
                                    class:positive={($investInfoMap[code]?.t8407OutBlock1?.체결수량 || 0) > 0}
                                    class:negative={($investInfoMap[code]?.t8407OutBlock1?.체결수량 || 0) < 0}
                                >{formatNumber($investInfoMap[code]?.t8407OutBlock1?.체결수량 || 0)}</td>
                                <td class="candle-cell">
                                    {@html $candleStore[code] ? 
                                        CandleStick({
                                            candle: $candleStore[code],
                                            width: 10,
                                            height: 20
                                        }) : '-'
                                    } 
                                </td>
                            {/if}
                        </tr>
                        {#if $selectedStocks[code] && $investInfoMap[code] && view_selected_stocks}
                            <tr class="info-row">
                                <td colspan="8">
                                    <div class="stock-detail button-group">
                                        <button class="detail-item button" on:click={() => handleDetailClick('시가총액')}>
                                            <span class="detail-label">시총:</span>
                                            <span class="detail-value">{formatNumber($investInfoMap[code]?.t3320OutBlock?.시가총액 || 0)}</span>
                                        </button>
                                        <button class="detail-item button" on:click={() => handleDetailClick('외국인')}>
                                            <span class="detail-label">외인:</span>
                                            <span class="detail-value">{$investInfoMap[code]?.t3320OutBlock?.외국인 || 0}</span>
                                        </button>
                                        <button class="detail-item button" on:click={() => handleDetailClick('배당수익율')}>
                                            <span class="detail-label">배당:</span>
                                            <span class="detail-value">{$investInfoMap[code]?.t3320OutBlock?.배당수익율 || 0}</span>
                                        </button>
                                        <button class="detail-item button" on:click={() => handleDetailClick('PER')}>
                                            <span class="detail-label">PER:</span>
                                            <span class="detail-value">{$investInfoMap[code]?.t3320OutBlock1?.PER || 0}</span>
                                        </button>
                                        <button class="detail-item button" on:click={() => handleDetailClick('ROE')}>
                                            <span class="detail-label">ROE:</span>
                                            <span class="detail-value">{$investInfoMap[code]?.t3320OutBlock1?.ROE || 0}</span>
                                        </button>
                                        <button class="detail-item button" on:click={() => handleDetailClick('tag')}>
                                            <span class="detail-value">{$investInfoMap[code]?.db?.tag || ''}</span>
                                        </button>
                                        <button class="detail-item button" on:click={() => handleDetailClick('업종구분명')}>
                                            <span class="detail-value">{$investInfoMap[code]?.db?.업종구분명 || ''}</span>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        {/if}
                        {#if showChart && $selectedStocks[code]}
                        <tr 
                            class="chart-row"
                            class:with-quarter-chart={toggleQuarterChart.includes(code)}
                        >
                            <td class="chart-cell" colspan="8">
                                <div class="chart-container">
                                    <div bind:this={chartElement} class="chart-element"></div>
                                </div>
                            </td>
                        </tr>
                        {/if}
                        {#if code && toggleQuarterChart && toggleQuarterChart.includes(code)}
                            <tr class="chart-row">
                                <td class="chart-cell" colspan="8">
                                    {#if $dartData?.quarterBalance?.[code]}
                                        <!-- 전달하는 데이터 확인 -->
                                        {#if Array.isArray($dartData.quarterBalance[code])}
                                            <SalesChart 
                                                revenueData={$dartData.quarterBalance[code]} 
                                                symbol={code}
                                            />
                                            <!-- 디버깅용 -->
                                            <!-- <pre>
                                                {JSON.stringify($dartData.quarterBalance[code], null, 2)}
                                            </pre> -->
                                        {:else}
                                            <div>Invalid data format</div>
                                        {/if}
                                    {:else}
                                        <div>Loading data...</div>
                                    {/if}
                                </td>
                            </tr>
                        {/if}
                    {/each}
                </tbody>
            </table>
        {/if}
    </div>
</div>


    <!-- 실시간 뉴스 -->
<div class="news-container">
    실시간 뉴스
    {#each news as item, i}
        {#if item && item.body}
            <div class="news-item">
                <button 
                    class="news-accordion-button"
                    on:click={() => toggleNews(item)}
                    class:active={selectedNews === item}
                >
                    <span class="news-time">
                        {item.body?.time ? `${item.body.time.slice(0,2)}:${item.body.time.slice(2,4)}` : ''}
                    </span>
                    <span class="news-title">
                        {item.body?.title || ''}
                    </span>
                </button>
            </div>
            {#if selectedNews === item}
                <div class="news-content" transition:slide>
                    {#if !item.content}
                        <div class="loading-text">뉴스 본문을 불러오는 중...</div>
                    {:else}
                        {@html sanitizeHtml(item.content)}
                    {/if}
                </div>
            {/if}
        {/if}
    {/each}
</div>


</div>
<style>
    .stock-container {
        position: relative;
        z-index: 1;          /* 메인 컨텐츠와 같은 레벨 */
        padding: 20px 0 0 0;
        background-color: #fff;
    }
    /* 키 입력 스타일 */

    
    .stock-tag.input-group {
        width: 80px;  /* 폭 넓히기 */
        height: 15px;
        font-size: 11px;
        padding: 0 4px;
        box-sizing: border-box;
    }
    .stock-input {
        height: 20px;
        width: 90px;
        font-size: 12px;
        padding: 0 4px;
        box-sizing: border-box;
    }
    
    
    input {
        height: 20px;  /* 입력창 높이 */
        box-sizing: border-box;
    }





    input {
        width: 100%;
        padding: 8px 30px 8px 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }

    

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }

    th, td {
        padding: 6px 8px;
        border-bottom: 1px solid #eee;
        white-space: nowrap;
    }

    th {
        background-color: #f8f9fa;
        font-weight: bold;
        text-align: center;
        position: sticky;
        top: 0;
        z-index: 1;
    }
    td {
        text-align: right;
    }

    .text-right {
        text-align: right;
    }
    
    
    .positive {
        color: #ff4444;
    }

    .negative {
        color: #2196f3;
    }



    /* ////////////////////////////////////////////////////////////////////////계좌 요약 테이블 스타일 */
    .accno-container {
        position: relative;
        max-height: 600px;
        overflow-y: auto;
        overflow-x: hidden;
        margin-top: 10px;  /* 버튼과의 간격 */
        z-index: 1;
    }
    
    
    /* ////////////////////////////////////////////////////////////////////////버튼 스타일 */
    .toggle-button, .load-button {
        padding: 1px 1px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 10px;
        transition: all 0.2s;
        height: 15px;
        line-height: 1;
        min-width: 30px;
        max-width: 100px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: #fff;        /* 텍스트 색상 */
    }

    .load-button.loading {
        background-color: #90a4ae;  /* 로딩 중일 때 색상 */
    }

    .toggle-button {
        background-color: #78909c;  /* 회색빛 파란색 */
    }

    .load-button {
        background-color: #607d8b;  /* 더 진한 회색빛 파란색 */
    }
    .button-row {
        background-color: #607d8b;  /* 더 진한 회색빛 파란색 */
    }
    .button-group {
        margin-top: 0.5rem;
        display: flex;
        gap: 6px;
    }
    .toggle-button:hover, .load-button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .toggle-button:active, .load-button:active {
        transform: translateY(0);
        opacity: 1;
    }

    .delete-button {
        background-color: #dc3545;  /* 빨간색 계열 */
    }
    
    .delete-button:disabled {
        background-color: #dc354580;
        cursor: not-allowed;
    }
    
    
    .button-row {
        display: flex;          /* Flexbox 사용 */
        flex-direction: row;    /* 가로 방향 정렬 */
        align-items: center;    /* 세로 중앙 정렬 */
        gap: 6px;              /* 버튼 간격 */
        margin: 4px 0;         /* 상하 여백 */
        padding: 4px;
        width: 100%;          /* 내부 여백 */
        background-color: #ffffff;  
    }
    button {
        align-self: flex-start;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        background-color: #007bff;
        color: white;
        cursor: pointer;
    }

    button:hover {
        background-color: #0056b3;
    }

    /* stock detail info */
    .stock-detail.button-group {
        display: flex;
        gap: 1px;
        margin: 0;
        padding: 0;
    }
    .detail-item.button {
        border: none;
        background: none;
        margin: 0;
        padding: 0;
        cursor: pointer;
        display: flex;
        align-items: left;
        /* gap: px; */
    }



    /* ////////////////////////////////////////////////////////////////////////종목 테이블 스타일 */
    .interest-container {
        display: flex;
        flex-direction: column;
        gap: 0;  /* 컴포넌트 간 간격 제거 */
    }
    .interest-stock-container {
        width: 100%;

    }
    .interest-stock-table {
        width: 100%;  /*또는 원하는 고정 너비*/
        max-width: 100%;
        /* margin: 0 auto; */
        
    }

    .detail-value-container {
        display: flex;
        align-items: center;
        justify-content: flex-end; /* 우측 정렬 */
        gap: 2px;
    }
    .stock-header-row {
        background-color: #f8f9fa;
        font-size: 8px;
        font-weight: bold;
        text-align: right;

    }
    .market-type, .stock-code, .stock-price, .stock-ratio, .stock-volume, .stock-cvolume {
        text-align: right;
        width: fit-content;
        padding: 2px 2px;
    }
    .stock-cvolume{
        width: 80px;
    }
    .market-type {

        font-size: 9px;
        min-width: 7px;
        text-align: center;
    }
    .stock-row.active {
        background-color: #e3e8ff;
    }
    .code-header {
        display: flex;
        align-items: center;
        justify-content: flex-start;  /* 왼쪽 정렬 */
    }
    .code-header select {
        width: 100%;
        padding: 2px 2px 2px 2px; /* 우측 패딩 증가 */
        border: none;
        background: transparent;
        font-size: inherit;
        font-weight: bold;
        cursor: pointer;
        appearance: none;
        text-align: right;
    }
    .stock-code {

        text-align: right;
        font-size: 5px;
        min-width: 18px;
        text-align: center;
    }

    .stock-name {
        text-align: left;

        /* 좌측 패딩 추가 */
        padding-left: 3px;
        margin: 0px 3px;
        font-size: 9px;
    }
    .stock-detail {
        display: flex;
        gap: 1px;
        padding: 1px 2px;
        align-items: center;
        justify-content: flex-start;  /* 왼쪽 정렬 */
    }
    


    
    .stock-row.owned-stock td {
        background-color: #fff3e0;  /* 연한 주황색 배경 */
    }

    .stock-row.owned-stock:hover td {
        background-color: #ffe0b2;  /* 호버 시 약간 진한 주황색 */
    }

    .stock-row.owned-stock.active td {
        background-color: #ffcc80;  /* 선택 시 더 진한 주황색 */
    }

   




    

    .detail-value {
        font-weight: 500;
        text-align: right;
    }





    .detail-item {
        display: flex;
        align-items: center;
        gap: 1px;
        min-width: 50px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .detail-item:hover {
        background-color: rgba(0, 0, 0, 0.05);
        padding: 0px 0px;
        margin: 0px 0px;

        border-radius: 4px;
    }

    .detail-label {
        color: #888;
        font-size: 5px;
        font-weight: 500;
    }

    .detail-value {
        padding: 0px 0px;
        margin: 0px 0px;
        color: #000;
        font-size: 9px;
        font-weight: 500;
    }



    /* 기존 스타일 유지 */
    .positive { color: #d24f45; }
    .negative { color: #1261c4; }
    /* text-align 추가 */
    .text-gradient {
        color: #3f51b5;  /* Google Blue */
        font-weight: 500;
        text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
    }
    .stock-tag-name {
        width: 80px;
        font-size: 10px;
    }
    /* 보유 종목 행 스타일 */
    
    

    .selected-count {
        color: #666;
        font-size: 13px;
    }

    
    .search-container {
        position: relative;
        width: 120px;

    }

    .search-results {
        position: absolute;
        top: 100%;
        left: 0;
        width: 100%;
        background: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        max-height: 200px;
        overflow-y: auto;
        margin-top: 2px;
        z-index: 1000;
    }

    .search-result-item {
        width: 100%;
        padding: 4px 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: none;
        background: none;
        cursor: pointer;
        text-align: left;
    }

    .search-result-item:hover {
        background-color: #f5f5f5;
    }

    .result-code {
        color: #666;
        font-size: 11px;
    }

    .result-name {
        color: #333;
        font-size: 11px;
    }
    .search-result-item.selected {
        background-color: #e3f2fd;
    }

    .search-result-item:hover {
        background-color: #f5f5f5;
    }
    

    .candle-cell {
        padding: 3px 3px;
        vertical-align: middle;
        width: 30px;
    }

    /* 차트 그리기 */
    .input-row.search-container {
        margin-right: 10px;
        /* gap: 10px; */
    }
    
    .input-group {
        position: relative;
        flex: 0 0 auto;        /* flex-grow: 0, flex-shrink: 0 */
        display: flex;
        align-items: center;
        font-size: 10px;
        height: 20px;
        margin: 0;             /* 마진 제거 */
        white-space: nowrap;   /* 텍스트 줄바꿈 방지 */ 
    }
    .input-group.tag {
        display: flex;
        flex-direction: row;
        gap: 4px;
        margin: 4px 0;
        padding: 2px;
        width: auto;          /* 자동 너비로 변경 */
        min-width: 60px;      /* 최소 너비 설정 */
        max-width: 80px;      /* 최대 너비 설정 */
        background-color: #ffffff;
    }
    .input-count {
        width: 50px;
        height: 18px;
        padding: 2px 4px;
        border: 1px solid #ddd;
        border-radius: 3px;
        font-size: 12px;
        text-align: center;
    }
    .select-period {
        height: 24px;
        padding: 2px 4px;
        border: 1px solid #ddd;
        border-radius: 3px;
        background-color: white;
        font-size: 12px;
        cursor: pointer;
    }
    .input-count:focus,
    .select-period:focus {
        outline: none;
        border-color: #4a90e2;
    }
    .select-period:hover {
        background-color: #f5f5f5;
    }
    /* 입력 요소의 화살표 버튼 스타일링 */
    .input-count::-webkit-inner-spin-button,
    .input-count::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type="checkbox"] {
        width: 16px;
        height: 16px;
        cursor: pointer;
    }
    /* td {
        padding: 2px 2px;
    } */
    /* 매매일지 스타일 **************************************************/
    .setup-trade-log-container {
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 0.5rem;
        margin-top: 0.3rem;
        background-color: #fff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        max-width: 100%;
        overflow: hidden;
    }
/* 스크롤 가능한 컨테이너 */
    .table-container {
        width: 100%;
        overflow-x: scroll;  /* auto -> scroll로 변경 */
        scrollbar-width: thin;  /* Firefox */
        scrollbar-color: #ddd transparent;  /* Firefox */
    }

    /* Webkit 브라우저용 스크롤바 스타일 */
    .table-container::-webkit-scrollbar {
        height: 8px;  /* 가로 스크롤바 높이 */
    }

    .table-container::-webkit-scrollbar-track {
        background: transparent;
    }

    .table-container::-webkit-scrollbar-thumb {
        background-color: #ddd;
        border-radius: 4px;
    }

    /* 테이블 스타일 */
    .trade-log-table {
        width: max-content;  /* 내용에 맞춰 너비 설정 */
        min-width: 100%;    /* 최소 너비는 컨테이너 크기 */
        border-collapse: collapse;
        font-size: 8px;
    }
   
    


    .trade-log-table tr:hover {
        background-color: #f8f9fa;  /* 행 호버 효과 */
    }
    
    
   
    .amount-korean {
    font-size: 6px;  /* 금액 한글 표시도 축소 */
    white-space: nowrap;
}
    /* 매매일지 입력 폼 스타일 */
    .trade-log-input-form {
        margin-bottom: 0.2rem;
        padding: 0.2rem;
        display: flex;
        flex-direction: column;
    }

    .input-row {
        display: flex;
        gap: 0.1rem;
        align-items: center;
        margin-bottom: 0.1rem;
        height: 1.2rem;  /* 0.8rem -> 1.2rem */
        gap: 0.5rem;  /* 간격 조정 */
        flex-wrap: nowrap;  /* 줄바꿈 방지 */
        width: 100%;  /* 전체 너비 사용 */
    }

    .trade-input {
        padding: 0 0.2rem;
        height: 1.2rem;
        font-size: 0.7rem;
        min-height: 1.2rem;
        line-height: 1.2rem;
        width: 200px;
        flex: 0 0 auto;  /* 크기 고정 */
    }

    .trade-input.quantity,
    .trade-input.price,
    .trade-input.amount,
    .trade-input.exchange {
        gap: 5rem;
    }
    .trade-input.quantity,
    .trade-input.price {
        width: 85px;
    }
    .gubun-input {
        width: 130px;  /* 너비 축소 */
    }
    .amount-korean {
        white-space: nowrap;  /* 텍스트 줄바꿈 방지 */
        font-size: 0.7rem;
        min-width: 80px;  /* 최소 너비 설정 */
    }
    .date-input,
    select.trade-input {
        width: 120px;  /* 날짜 입력 폼 너비 축소 */
        height: 1.2rem;  /* 0.8rem -> 1.2rem */
        padding: 0 0.2rem;
        min-height: 1.2rem;
        font-size: 0.6rem;  /* 0.3rem -> 0.7rem */
        font-weight: 500;
    }

    .add-trade-button {
        padding: 0 0.2rem;
        height: 1.2rem;  /* 0.8rem -> 1.2rem */
        font-size: 0.7rem;  /* 0.3rem -> 0.7rem */
        line-height: 1.2rem;
        min-height: 1.2rem;
        width: 3rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    
    .radio-group {
        display: flex;
        gap: 1rem;
        align-items: center;
        height: 1.2rem;
        justify-content: flex-end;  /* 우측 정렬 추가 */
        margin-left: auto;  /* 왼쪽 여백을 자동으로 설정하여 오른쪽으로 밀기 */
    }

    .radio-label {
        display: flex;
        align-items: center;
        gap: 0.1rem;
        font-size: 0.7rem;
        cursor: pointer;
    }

    .radio-input {
        margin: 0;
        width: 0.8rem;
        height: 0.8rem;
    }

    .radio-text {
        font-size: 0.5rem;
        line-height: 1.2rem;
    }
    .trade-red {
        color: #f44336;  /* 입금: 적색 */
    }

    .trade-blue {
        color: #2196f3;  /* 출금: 청색 */
    }

    /* 입력 필드 포커스 시에도 색상 유지 */
    .trade-red:focus {
        color: #f44336;
        border-color: #f44336;
    }

    .trade-blue:focus {
        color: #2196f3;
        border-color: #2196f3;
    }
    .text-blue {
        color: blue;  /* 출금: 청색 */
        font-weight: 500;
    }
    .trade-log-table-title {
        font-size: 11px;
        font-weight: 500;
        color: #2c3e50;
        margin: 0.5rem 0 0.2rem 0;
        padding: 0.2rem 0.5rem;
        background-color: #f5f5f5;
        border: 1px solid #eee;
        border-bottom: none;
        border-radius: 4px 4px 0 0;
    }
    .trade-date-cell {
        position: relative;  /* 변경 */
        padding-left: 12px !important;  /* 삭제 버튼 공간 확보 */
        width: 90px;
        /* font-size: 10px; */
    }

    .delete-badge {
        padding: 2px 6px;
        margin-right: 4px;
        border: none;
        border-radius: 4px;
        background-color: red;
        color: white;
        font-size: 12px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
 
    .edit-trade {
        background-color: #f44336;
    }
    .edit-badge {
        padding: 2px 6px;
        margin-right: 4px;
        border: none;
        border-radius: 4px;
        background-color: #2196f3;
        color: white;
        font-size: 12px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .edit-badge:hover {
        background-color: #1976d2;
    }
    .update-color {
        background-color: #4caf50;
        color: white;
    }

    /* ////////////////////////////////////////////////////////////////////////차트 스타일 */
    
    .chart-row {
        position: relative;
        width: 100%;
        height: 180px;
    }

    .chart-cell {
        position: relative;
        padding: 0 !important;
        width: inherit;  /* 부모 테이블의 너비 상속 */
        height: inherit;
    }
    .chart-row.with-quarter-chart {
        height: 210px;
    }

    .chart-container {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100%;
        height: 100%;
    }

    /* 반응형 높이 조정 */
    @media (max-width: 1200px) {
        .chart-row {
            height: 250px;
        }
        /* .chart-cell { height: 250px; } */
        .chart-row.with-quarter-chart {
            height: 300px;
        }
    }

    @media (max-width: 768px) {
        .chart-row {
            height: 180px;
        }
        /* .chart-cell { height: 210px; } */
        .chart-row.with-quarter-chart {
            height: 210px;
        }
    }

    
    .chart-element {
        width: 100%;
        height: 100%;
    }
    .sales-chart-wrapper {
        width: 100%;
        height: 100%;
        border: 1px solid red; /* 디버깅용 테두리 */
    }
    
    .badge {
        display: inline-block;
        padding: 1px 4px;
        font-size: 8px;
        font-weight: 500;
        line-height: 1;
        color: #fff;
        background-color: #2c3e50;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        margin: 0 4px;
        white-space: nowrap;  /* 줄바꿈 방지 */
        overflow: visible;    /* 내용이 넘쳐도 보이게 */
        text-overflow: clip;  /* 텍스트 자르지 않음 */
        user-select: none;  /* 텍스트 선택 방지 */
    }

    .badge:hover {
        background-color: #34495e;
    }
    .badge.active {
        background-color: #f44336;
    }
    
    
    
    /* 전체 폰트 크기 조정 */
    :global(body) {
        font-size: 16px;
    }

    :global(button) {
        font-size: 16px;
        padding: 8px 16px;
    }

    :global(table) {
        font-size: 16px;
    }

    :global(th), :global(td) {
        padding: 12px;
    }
    

    .loading {
        background-color: #f0f0f0;
        color: #666;
        cursor: not-allowed;
    }
    .loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.7);
    }

    .loading::before {
        content: '로딩중...';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1;
        color: #333;
    }
    
    /* ////////////////////////////////////////////////////////////////////////양도소득 상세 표시 */
    .detail-row {
        background-color: #f8f9fa;
    }
    .detail-content {
        padding: 1rem;
        background-color: #f8f9fa;
    }
    .no-data {
        text-align: center;
        color: #666;
        padding: 1rem;
    }
    
    .detail-item {
        display: flex;
        align-items: center;
        /* gap: 0.5rem; */
    }
    


    
    /* ////////////////////////////////////////////////////////////////////////뉴스 리스트 컨테이너 */
    .news-container {
        width: 100%;
    }

    /* 뉴스 아이템 */
    .news-item {
        width: 100%;
        border-bottom: 1px solid #eee;
    }

    /* 뉴스 버튼 */
    .news-accordion-button {
        width: 100%;
        padding: 8px 12px;
        background: none;
        border: none;
        text-align: left;
        cursor: pointer;
        display: flex;
        align-items: center;
        width: 100%;
        padding: 8px 12px;
        background: none;
        border: none;
        text-align: left;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        box-sizing: border-box;
        transition: background-color 0.2s ease;
    }
    /* 호버 효과 */
    .news-accordion-button:hover {
        background-color: #f0f7ff;  /* 매우 연한 파란색 */
    }

    .news-accordion-button:hover .news-time {
        color: #2196f3;  /* 호버 시 시간 텍스트 색상 */
    }

    .news-accordion-button:hover .news-title {
        color: #1976d2;  /* 호버 시 제목 텍스트 색상 */
    }

    /* 선택된 상태 */
    .news-accordion-button.active {
        background-color: #e3f2fd;  /* 연한 파란색 */
    }
    /* 뉴스 시간 */
    .news-time {
        flex: 0 0 45px;  /* 고정 너비 */
        color: #666;
        font-family: monospace;

    }

    /* 뉴스 제목 */
    .news-title {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        padding-right: 12px;
        color: #333;
    }

    /* 뉴스 내용 */
    .news-content {
        width: 100%;
        padding: 12px;
        background-color: #f8f9fa;
        font-size: 12px;
        line-height: 1.5;
        border-top: 1px solid #eee;
        box-sizing: border-box;
        word-break: break-word;
        overflow-wrap: break-word;
    }

    /* 뉴스 내용 HTML 요소 */
    .news-content :global(p) {
        margin: 0 0 8px 0;
        overflow-wrap: break-word;
        word-break: break-word;  /* 긴 단어 줄바꿈 */
    }

    .news-content :global(img) {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 0 auto;  /* 이미지 중앙 정렬 */
    }
    table {
        width: fit-content;  /* 내용에 맞게 테이블 너비 조정 */
        min-width: auto;     /* 최소 너비 제한 해제 */
        border-collapse: collapse;
    }

    td:not(.chart-cell) {
        padding: 0px 5px;  /* 패딩 최소화 */
        white-space: nowrap;  /* 줄바꿈 방지 */
        width: fit-content;  /* 내용에 맞게 너비 조정 */
    }
    
    /* 로딩 텍스트 */
    .loading-text {
        width: 100%;
        padding: 10px;
        text-align: center;
        color: #666;
        font-style: italic;
        box-sizing: border-box;
    }

    .accounts-page {
        padding: 20px;
    }
    .investment-page {
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
    }

    
    /* 모바일 대응 */
    @media (max-width: 768px) {
        .chart-row, .chart-cell {
            height: 180px;
        }
        /* toggleQuarterChart가 true일 때 높이 증가 */
        .chart-row.with-quarter-chart {
            height: 210px;
        }
        
       

        .chart-container {
            max-width: 100%;
            overflow-x: hidden;  /* 가로 스크롤 방지 */
        }

        .chart-cell {
            max-width: 100vw;
            overflow-x: hidden;
        }

        .badge {
            font-size: 8px;
            padding: 1px 3px;
        }
    /* 매매 일지 테이블 스타일 */
    .trade-log-table td,
        .trade-log-table th {
            font-size: 0.7rem;
            padding: 4px;
        }

        .trade-log-table.date {
            min-width: 50px;
            max-width: 50px;
        }

        .trade-log-table.name {
            min-width: 50px;
            max-width: 70px;
            left: 50px;
        }

        /* 스크롤바 터치 최적화 */
        .table-container {
            overflow-x: scroll;
            scrollbar-width: thin;
        }

        .table-container::-webkit-scrollbar {
            height: 4px;  /* 모바일에서는 더 얇게 */
        }
    }
</style>