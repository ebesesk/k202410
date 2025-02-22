// 양도소득 계산 API 호출 함수
import fastapi from '$lib/api';

export async function calculateTaxGains(code, date) {
    let year = date.slice(0, 4);
    console.log('calculateTaxGains:', code, year);
    let params = {
        code: code, 
        year: year
    }
    
    return new Promise((resolve, reject) => {
        fastapi('get', '/stock/tax', params, 
            (json) => {
                console.log('json:', json);
                resolve(json);  // API 응답 데이터 반환
            },
            (error) => {
                console.error('API 에러:', error);
                reject(error);
            }
        );
    });
}

// 다른 주식 관련 API 함수들도 여기에 추가 가능
export async function getStockInfo(code) {
    // ...
}

export async function getInvestmentInfo(code) {
    // ...
}