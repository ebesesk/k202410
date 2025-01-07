<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { browser } from '$app/environment';
    import {onDestroy} from 'svelte';    
    import { slide } from 'svelte/transition';  // slide 트랜지션 추가
    import fastapi from '$lib/api';
    import { username } from '$lib/store';
    import { accno_list, accno_codes, key, selectedStocks, investInfoMap, candleStore, chartDataStore, sortedCodes} from "$lib/stores/stock";
    import { get } from 'svelte/store';
    import { access_token } from '$lib/store';

    import { createChart } from 'lightweight-charts';
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    
  
    onMount(async () => {
        if (browser && $key) {
            getInterestStocks();
            // $chartDataStore = {};
        }
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
            // console.log('accno_codes:', $accno_codes);
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
            console.log('stocks:', _stocks)
            console.log('accnoCodes:', accnoCodes)
            console.log('shcodes:', shcodes)
            console.log('multi_price:', multi_price)
            
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
    // 숫자 포맷팅 함수
    function formatNumber(num) {
        try {
            if (num === undefined || num === null) return '0';
            return new Intl.NumberFormat('ko-KR').format(num);
        } catch (error) {
            console.error('formatNumber error:', error);
            return '0';
        }
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
            const investinfo_list = json.investinfo_list;
            for (const investinfo of investinfo_list) {
                let code = investinfo.t3320OutBlock1.기업코드.slice(1, 7);
                $investInfoMap[code].t3320OutBlock = investinfo.t3320OutBlock;      // 종목코드로 투자 정보 조회
                $investInfoMap[code].t3320OutBlock1 = investinfo.t3320OutBlock1;    // 종목코드로 투자 정보 조회
                $investInfoMap = {...$investInfoMap};  // 반응성 트리거
            }
            console.log('investInfoMap:', $investInfoMap);
            loadingMultiInvestInfo = false;
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
                    "sujung_yn": "Y"
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
        if (!browser || !chartContainers.get(code)) {
            console.error('차트 초기화 실패: browser 또는 container 없음', {
                browser,
                container: chartContainers.get(code),
                code
            });
            return;
        }
        
        try {
            const container = chartContainers.get(code);
            
            // 기존 차트가 있으면 제거
            if (charts.has(code)) {
                charts.get(code).remove();
                charts.delete(code);
                candleSeriesMap.delete(code);
                volumeSeriesMap.delete(code);
            }

            const chartInstance = createChart(container, {
                // width: container.clientWidth,   // 컨테이너 너비에 맞춤
                // height: container.clientHeight, // 컨테이너 높이에 맞춤
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
                // 차트 영역 분리
                rightPriceScale: {
                    scaleMargins: {
                        top: 0.1,
                        bottom: 0.3,  // 캔들차트 아래 여백
                    },
                    autoScale: true,
                    mode: 1,  // 0: 일반, 1: 로그 스케일
                    
                    borderVisible: false,
                    entireTextOnly: true,
                    drawTicks: false,
                },
                handleScroll: {
                    mouseWheel: false,  // 마우스 휠 스크롤 비활성화
                    pressedMouseMove: false,  // 마우스 드래그 비활성화
                    horzTouchDrag: true,  // 터치 드래그 비활성화
                    vertTouchDrag: true,  // 세로 터치 드래그 비활성화
                },
                handleScale: {
                    mouseWheel: false,  // 마우스 휠 스크롤 비활성화
                    pressedMouseMove: false,  // 마우스 드래그 비활성화
                    pinch: false,  // 터치 확대/축소 비활성화
                    touch: false,  // 터치 확대/축소 비활성화
                },       // 확대/축소 비활성화
                timeScale: {
                    
                    rightOffset: 3,
                    fixLeftEdge: false,    // 왼쪽 고정
                    fixRightEdge: false,   // 오른쪽 고정
                    // lockVisibleTimeRangeOnResize: true,  // 리사이즈시 시간 범위 고정
                    lockVisibleTimeRangeOnResize: true,  // 리사이즈시 보이는 범위 고정
                    barSpacing: 5,       // 봉 간격
                    minBarSpacing: 2,     // 최소 봉 간격
                    rightBarStaysOnScroll: true,  // 스크롤 시 오른쪽 봉 유지
                },
                // crosshair: {
                // mode: CrosshairMode.Normal,  // 십자선 모드
                // },
            });
            // 차트 크기 자동 조정
            new ResizeObserver(() => {
                chartInstance.applyOptions({
                    width: container.clientWidth,
                    height: container.clientHeight,
                });
            }).observe(container);

            // 캔들스틱 시리즈
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

            // 거래량 시리즈 (별도의 프라이스 스케일 사용)
            const volumeSeries = chartInstance.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',
                    precision: 0,
                },
                priceScaleId: 'volume',  // 별도의 프라이스 스케일 ID
                scaleMargins: {
                    top: 0.7,  // 거래량 차트는 아래쪽 30% 영역 사용
                    bottom: 0.05,
                },
            });

            // 거래량 차트의 Y축 설정
            chartInstance.priceScale('volume').applyOptions({
                scaleMargins: {
                    top: 0.7,    // 위쪽 70% 여백
                    bottom: 0.05 // 아래쪽 5% 여백
                },
                visible: true,   // Y축 표시
                autoScale: true  // 자동 스케일링
            });

            // Map에 저장
            charts.set(code, chartInstance);
            candleSeriesMap.set(code, candleSeries);
            volumeSeriesMap.set(code, volumeSeries);

            // 리사이즈 핸들러
            const handleResize = () => {
                chartInstance.applyOptions({
                    width: container.clientWidth
                });
            };
            window.addEventListener('resize', handleResize);
            

            

            return () => {
                window.removeEventListener('resize', handleResize);
            };

        } catch (error) {
            console.error('차트 초기화 실패:', error);
        }
    }

    // 차트 데이터 업데이트 함수
    function updateChartData(data) {
        if (!data || !data.data) return;
        
        try {
            const code = stock?.db?.종목코드;
            console.log('차트 데이터 업데이트:', code, data);

            const candleSeries = candleSeriesMap.get(code);
            const volumeSeries = volumeSeriesMap.get(code);
            
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
                .slice(-qrycnt);  // 최근 qrycnt개만 사용

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
                console.log('json:', json);
                $investInfoMap[newStockCode] = json[newStockCode];
                $investInfoMap = {...$investInfoMap};
                console.log('investInfoMap:', $investInfoMap);
                newStockCode = '';
            });
        }
    }



    // 검색 결과 저장 변수
    let searchResults = [];
    let searchTimeout;

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
        if (stock && tag && tag.length > 0 && tag !== stock.db.tag) {
            let code = stock['t3320OutBlock1']['기업코드'].slice(1, 7);
            // let tag = stock.db.tag;
            console.log('code:', code);
            console.log('tag:', tag);
            let params = {
                code: code,
                tag: tag
            }
            fastapi('post', '/stock/update_interest_stock_tag'+'?key='+$key, params, (json) => {
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
// /////////////////////////////////////////////////////////////////////////////////////////

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

// 직접 웹소켓 연결 /////////////////////////////////////////////////////////////////////////////////////////
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

    // 웹소켓 연결 종료 함수
    function closeDirectWss(type = 'direct') {
        wsConnections.update(connections => {
            const newConnections = new Map(connections);
            const ws = newConnections.get(type);
            if (ws) {
                ws.close();
                newConnections.delete(type);
                console.log('WebSocket 연결 종료:', type);
            }
            return newConnections;
        });
    }

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
        console.log('handleNewsMessage:', data);
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
        const index = $accno_codes.indexOf(data.body.shcode) + 3;
        const peyonga = $accno_list[index][23];
        const peyongason = $accno_list[index][24];
        
        // 개별 종목 정보 업데이트
        $accno_list[index][22] = data.body.price;
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

//// 직접 웹소켓 연결 끝 /////////////////////////////////////////////////////////////////////////////////////////
//// 테스트 웹소켓 연결 시작 /////////////////////////////////////////////////////////////////////////////////////////

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
            tr_cd: tr_cd,
            code: code
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

            // 웹소켓 연결 이벤트 처리
            testWss.onopen = () => {
                console.log('WebSocket 연결됨:', url);
                addWebSocketConnection('test', testWss);
            };

            testWss.onmessage = (event) => {
                const realData = JSON.parse(event.data);
                // console.log('실시간 데이터:', realData);
                // 여기서 차트 업데이트 등 처리
                // updateChartWithRealData(realData);
                // updateRealtimeChart(realData);
                handleWebSocketMessage(realData);
            };

            testWss.onclose = () => {
                console.log('WebSocket 연결 종료');
            };

            testWss.onerror = (error) => {
                console.error('WebSocket 오류:', error);
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

    // // 종목 클릭 시 WebSocket 연결
    // async function handleStockClick(_code) {
    //     // ... 기존 코드 ...

    //     // WebSocket 연결
    //     if (showChart) {
    //         await connectWebSocket(_code);
    //     }

    //     // ... 기존 코드 ...
    // } 


//// 테스트 웹소켓 연결 끝 /////////////////////////////////////////////////////////////////////////////////////////


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
// 상세 정보 끝 /////////////////////////////////////////////////////////////////////////////////////////

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


    // 컴포넌트 언마운트 시 연결 종료
    onDestroy(() => {
        closeDirectWss();   // WebSocket 연결 종료

        charts.forEach(chart => chart.remove());
        charts.clear();
        candleSeriesMap.clear();
        volumeSeriesMap.clear();
        chartContainers.clear();
    });


    
</script>

<!-- 키 입력 폼 -->
 
<div class="accno-container">
    <div class="input-container">
        
        <!-- APP KEY 입력 그룹 -->
        <div class="input-group">
            {#if isSetupKey}
                <input 
                    class="input-group input-field"
                    type="text" 
                    bind:value={cname} 
                    placeholder="cname를 입력하세요"
                    >    
                <input 
                    class="input-group input-field"
                    type="text" 
                    bind:value={appkey} 
                    placeholder="appkey를 입력하세요"
                >   
                <input 
                    class="input-group input-field"
                    type="text" 
                    bind:value={appsecretkey} 
                    placeholder="appsecretkey를 입력하세요"
                >   
                <input 
                    class="input-group key-input"
                    type="password" 
                    bind:value={$key} 
                    placeholder="키를 입력하세요"
                    disabled={isLoading}
                >
                
                <button 
                    class="clear-button" 
                    on:click={clearKey}
                    title="키 초기화"
                >×</button>
            {/if}
        </div>

        <!-- 설정 계좌조회 버튼 그룹 -->
        <div class="button-group">
            {#if isSetupKey}
            <button 
                class="action-button active-wss"
                on:click={setupLsOpenApiDb}
            >
                설정
            </button>
            {:else}
            <button 
                class="action-button"
                on:click={isSetupKey = !isSetupKey}
            >
                설정
            </button>
            {/if}
            
            
            <button 
                class="action-button"
                class:loading={isLoading}
                on:click={fetchAccnoList}
                disabled={!$key}
            >
                {#if isLoading}
                    조회중...
                {:else}
                    계좌조회
                {/if}
            </button>
        </div>

    </div>

    <!-- 계좌조회 테이블 -->
    {#if $accno_list.length > 0}
        <div class="accno-tables-container">
            <div class="table-scroll">
                <table class="accno-summary-table">
                    <thead>
                        <tr>
                            <th class="text-right">추정순자산</th>
                            <th class="text-right">평가손익</th>
                            <th class="text-right">매입금액</th>
                            <th class="text-right">추정D2예수금</th>
                            <th class="text-right">평가금액</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            {#each $accno_list[1] as value, i}
                                {#if $accno_list[0][i] !== 'CTS_종목번호'}
                                    <td class="text-right">{formatNumber(value)}</td>
                                {/if}
                            {/each}
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="table-scroll accno-table-scroll">
                <table class="stock-table accno-table">
                    <thead>
                        <tr>
                            <!-- <th class="text-right">종목번호</th> -->
                            <th class="text-right">종목명</th>
                            <th class="text-right">잔고수량</th>
                            <th class="text-right">매도가능수량</th>
                            <th class="text-right">평균단가</th>
                            <th class="text-right">매입금액</th>
                            <th class="text-right">현재가</th>
                            <th class="text-right">평가금액</th>
                            <th class="text-right">평가손익</th>
                            <th class="text-right">수익율</th>
                            <th class="text-right">수수료</th>
                            <th class="text-right">제세금</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each $accno_list.slice(3) as row}
                            <tr>
                                <!-- <td class="text-right">
                                    <button 
                                        class="link-button" 
                                        on:click={() => searchInvestInfo(row[0], row[18])}
                                    >
                                        {row[0]}
                                    </button>
                                </td> -->
                                <td class="text-right text-2196f3">{row[18]}</td>
                                <td class="text-right">{formatNumber(row[2])}</td>
                                <td class="text-right">{formatNumber(row[3])}</td>
                                <td class="text-right">{formatNumber(row[4])}</td>
                                <td class="text-right">{formatNumber(row[5])}</td>
                                <td class="text-right">{formatNumber(row[22])}</td>
                                <td class="text-right">{formatNumber(row[23])}</td>
                                <td class="text-right" class:positive={row[24] > 0} class:negative={row[24] < 0}>
                                    {formatNumber(row[24])}
                                </td>
                                <td class="text-right" class:positive={parseFloat(row[25]) > 0} class:negative={parseFloat(row[25]) < 0}>
                                    {row[25]}%
                                </td>
                                <td class="text-right">{formatNumber(row[26])}</td>
                                <td class="text-right">{formatNumber(row[27])}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>

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
                    on:click={closeDirectWss}
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
                        class="input-group text-input stock-tag"
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
                            <div class="chart-controls">
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
                {#if searchResults.length > 0}
                    <div class="search-results">
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
                            on:click={() => isSelectMode ? toggleStockSelection(code) : handleStockClick(code)}
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
                            <td class="stock-name text-gradient text-right">{$investInfoMap[code]?.db?.한글기업명}</td>
                            {#if $investInfoMap[code]?.t8407OutBlock1}
                                <td class="text-right stock-price"
                                    class:positive={($investInfoMap[code]?.t8407OutBlock1?.등락율 || 0) > 0}
                                    class:negative={($investInfoMap[code]?.t8407OutBlock1?.등락율 || 0) < 0}
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
                            <tr class="chart-row">
                                <td class="chart-cell" colspan="8">
                                    <div class="chart-container">
                                        <div bind:this={chartElement} class="chart-element"></div>
                                    </div>
                                </td>
                            </tr>
                        {/if}
                    {/each}
                </tbody>
            </table>
        {/if}
    </div>
</div>



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



<style>
    
    /* 키 입력 스타일 */

    .key-input {
        width: 80px;
        padding: 2px 4px;
        font-size: 10px;
    }
    .input-field {
        border: 1px solid #ccc;
        border-radius: 3px;
    }
    
    .stock-tag.input-group {
        width: 80px;  /* 폭 넓히기 */
        height: 15px;
        font-size: 11px;
        padding: 0 4px;
        box-sizing: border-box;
    }
    .stock-input {
        height: 20px;
        width: 60px;
        font-size: 12px;
        padding: 0 4px;
        box-sizing: border-box;
    }
    .input-group {
        position: relative;
        flex: 1;
        display: flex;
        align-items: center;
        font-size: 10px;
        height: 20px;
    }
    
    input {
        height: 20px;  /* 입력창 높이 */
        box-sizing: border-box;
    }




    .action-button {
        flex: 1;
        padding: 8px 12px;
        font-size: 13px;
        border: none;
        border-radius: 4px;
        background-color: #f0f0f0;
        color: #333;
        cursor: pointer;
        transition: all 0.2s;
        min-width: 0;
        white-space: nowrap;
    }

    .active-wss {
        background-color: #4CAF50;
        color: white;
    }

    .action-button:hover {
        opacity: 0.9;
    }

    .action-button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }

    input {
        width: 100%;
        padding: 8px 30px 8px 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }

    .clear-button {
        position: absolute;
        right: 5px;
        background: none;
        border: none;
        color: #666;
        font-size: 18px;
        padding: 0 8px;
    }

    

    .table-scroll {
        overflow-x: auto;
        margin-bottom: 15px;
        background: white;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
        width: 100%;
    }
    .accno-tables-container {
        margin-top: 0px;
    }
    
    .accno-summary-table {
        width: 100%;  /* 전체 너비 사용 */
        table-layout: fixed;  /* 고정 레이아웃 */
        border-collapse: collapse;
        margin: 0;
        padding: 0;
    }
    /* 셀 패딩 추가로 숫자가 너무 붙지 않도록 */
    .accno-summary-table th,
    .accno-summary-table td {
        padding: 2px 4px;  /* 좌우 패딩 추가 */
    }
    .accno-table th:nth-child(1),  /* 종목명 열의 위치에 맞게 조정 */
    .accno-table td:nth-child(1) {
        position: sticky;
        left: 0;
        background-color: white;
        z-index: 1;
        border-right: 1px solid #eee;
        min-width: 80px;  /* 종목명 최소 너비 */
    }
    .accno-table th:nth-child(1) {
        background-color: #f8f9fa;
        z-index: 2;
    }

    /* 호버 효과 시 배경색 */
    .accno-table tr:hover td:nth-child(1) {
        background-color: #f5f5f5;
    }

    /* 각 열의 너비 설정 */
    .accno-table th,
    .accno-table td {
        padding: 6px 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* 계좌 테이블 스크롤 컨테이너 */
    .accno-table-scroll {
        width: 100%;
        max-width: 100%;
        overflow-x: auto;
        margin: 0;
        padding: 0;
        background: white;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        -webkit-overflow-scrolling: touch;  /* iOS 스크롤 부드럽게 */
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

    .button-group {
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
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 8px 0;
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
        align-items: center;
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

        font-size: 8px;
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
        font-size: 8px;
        min-width: 30px;
        text-align: center;
    }

    .stock-name {
        text-align: left;

        /* 좌측 패딩 추가 */
        padding-left: 3px;
        margin: 0px 3px;
        /* font-size: 7px; */
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
        color: #666;
        font-size: 7px;
        font-weight: 500;
    }

    .detail-value {
        padding: 0px 0px;
        margin: 0px 0px;
        color: #333;
        font-size: 9px;
        font-weight: 500;
    }

    .text-right {
        text-align: right;
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
        width: 120px;
        font-size: 10px;
    }
    /* 보유 종목 행 스타일 */
    
    

    .selected-count {
        color: #666;
        font-size: 13px;
    }

    
    .search-results {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        z-index: 1000;
        margin-top: 4px;
    }

    .search-result-item {
        width: 100%;
        padding: 8px 12px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: none;
        background: none;
        text-align: left;
    }

    .search-result-item:hover {
        background-color: #f5f5f5;
    }

    .result-code {
        color: #666;
        font-size: 0.9em;
    }

    .result-name {
        font-weight: bold;
        margin-left: 8px;
    }

    
    

    .candle-cell {
        padding: 3px 3px;
        vertical-align: middle;
        width: 30px;
    }

    /* 차트 그리기 */

    .input-container {
        margin: 10px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
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
    td {
        padding: 2px 2px;
    }
    
    
    
    
   
    
    
    
    /* ////////////////////////////////////////////////////////////////////////차트 스타일 */
    
    .chart-row {
        position: relative;
        width: 100%;
        height: 200px;
    }

    .chart-cell {
        position: relative;
        padding: 0 !important;
        width: inherit;  /* 부모 테이블의 너비 상속 */
        height: inherit;
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
        .chart-cell { height: 250px; }
    }

    @media (max-width: 768px) {
        .chart-cell { height: 200px; }
    }

    @media (max-width: 480px) {
        .chart-cell { height: 180px; }
    }
    .chart-element {
        width: 100%;
        height: 100%;
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
        padding: 0px 0px;  /* 패딩 최소화 */
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

    
    /* 모바일 대응 */
    @media (max-width: 768px) {
        .chart-row, .chart-cell {
            height: 200px;
        }
        
        .chart-element {
            height: 180px;
            width: 100vw;  /* 뷰포트 너비에 맞춤 */
            max-width: 100%;  /* 부모 요소 너비를 넘지 않도록 */
        }

        .chart-container {
            max-width: 80%;
            overflow-x: hidden;  /* 가로 스크롤 방지 */
        }

        .chart-cell {
            max-width: 100vw;
            overflow-x: hidden;
        }



       
    }
</style>