import { key, dartData } from "$lib/stores/stock";
import { get } from 'svelte/store';
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
        key: get(key),
    }
    fastapi('get', url, params, (json) => {
        console.log(json);
    });
}
// 문자열을 숫자로 변환하는 함수
export const stringToNumber = (str) => {
    if (typeof str === 'string') {
        // 쉼표 제거하고 소수점을 올바르게 처리
        const cleanStr = str.replace(/,/g, '').replace(/[^0-9.-]/g, '');
        
        // 마지막 두 자리가 소수점이었다면 처리
        if (cleanStr.length > 2) {
            const mainPart = cleanStr.slice(0, -2);
            const decimalPart = cleanStr.slice(-2);
            return Math.floor(parseFloat(mainPart + '.' + decimalPart));
        }
        
        return Math.floor(parseFloat(cleanStr));
    }
    return Math.floor(Number(str));
};

export function getQuarterBalanceSheet(symbol, reload=false) {
    const url = '/stock/dart/balance-sheet'
    const params = {
        key: get(key),
        symbol: symbol,
        reload: reload,
    }
    fastapi('get', url, params, (json) => {
        console.log('json:', json);
        // 스토어 업데이트
        // $investInfoMap[symbol].quarter = json.quarter;
        
        // console.log('저장된 데이터:', $investmentStore);

        let _quarter = [];
        for (let [_key, _value] of Object.entries(json.quarter)) {
            if (_value[0] && _value[0].toString().startsWith('20')) {
                // console.log('item:', _key, _value);
                let dateStr = _value[0].toString();
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
                // console.log('formattedDate:', formattedDate);
                // console.log('item[10]:', item[10]);
                // let value = Number(_value[10].toString().replace(/,/g, ''))/100000000;
                let value = Math.floor(stringToNumber(_value[10])/1000000);
                // console.log('value:', value);
                _quarter.push({
                    time: formattedDate,
                    value: value, 
                    color: 'rgba(128, 128, 128, 0.5)'
                });
            }
            // console.log('_quarter:', _quarter);
        }

        // console.log('_quarter:', _quarter);
        // 시간순으로 정렬
        _quarter.sort((a, b) => {
            const timeA = new Date(a.time).getTime();
            const timeB = new Date(b.time).getTime();
            return timeA - timeB;
        });
        // quarterBalance[symbol] = _quarter;
        // store 업데이트
        dartData.update(currentData => ({
            ...currentData,
            quarterBalance: {
                ...(currentData?.quarterBalance || {}),
                [symbol]: _quarter
            }
        }));
        // quarterBalance[symbol] = _quarter;
        // console.log('quarterBalance:', get(dartData).quarterBalance);
        // if (!toggleQuarterChart.includes(symbol)) {
        //     toggleQuarterChart.push(symbol);
        // } else {
        //     toggleQuarterChart = toggleQuarterChart.filter(s => s !== symbol);
        // }
    });
}

function getBalanceSheet(symbol) {
    const url = '/stock/dart/balance-sheet'
    const params = {
        key: get(key),
        symbol: symbol,
    }
    fastapi('get', url, params, (json) => {
        console.log('json:', json);
        // 스토어 업데이트
        investmentStore.update(currentData => ({
            ...currentData,  // 기존 데이터 유지
            quarterBalanceSheet: {
                ...currentData.quarterBalanceSheet,
                [symbol]: json.report_quarter
            }
        }));
        
        // // 또는 setBalanceSheet 메서드 사용시
        // $investmentStore.setQuarterBalanceSheet(report_quarter);
        
        console.log('저장된 데이터:', get(investmentStore));
    });
}