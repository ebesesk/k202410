export function delSpecialCharacter(text) {
    if (!text) return text;
    
    // 문자열 앞뒤 공백 제거
    text = text.trim();
    
    // 정규식 패턴 배열
    const patterns = [
        /[|\\{}]/g,          // 파이프와 중괄호
        /[\[\]/?]/g,         // 대괄호와 슬래시
        /[.,;:!]/g,          // 구두점
        /[*~`^]/g,          // 특수 기호
        /[+<>@#$%&=]/g,     // 연산자와 특수 문자
        /['"]/g,           // 따옴표
        /[-_]/g,            // 하이픈과 언더스코어
        /\s+/g,             // 연속된 공백
        /_+/g               // 연속된 언더스코어
    ];
    
    // 각 패턴에 대해 공백으로 치환
    patterns.forEach(pattern => {
        text = text.replace(pattern, ' ');
    });
    
    // 최종 문자열 처리: 앞뒤 공백 제거 후 남은 공백을 언더스코어로 변환
    return text.trim().replace(/\s+/g, '_');
}

export function numberToKorean(number) {
    const units = ['', '만', '억', '조'];
    const digits = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
    const positions = ['', '십', '백', '천'];
    
    if (number === 0) return '영';
    
    let result = '';
    let unitIndex = 0;
    
    while (number > 0) {
        let segment = number % 10000;
        let segmentResult = '';
        
        for (let i = 0; segment > 0; i++) {
            let digit = segment % 10;
            if (digit !== 0) {
                segmentResult = (i > 0 && digit === 1 ? '' : digits[digit]) + positions[i] + segmentResult;
            }
            segment = Math.floor(segment / 10);
        }
        
        if (segmentResult !== '') {
            result = segmentResult + (unitIndex > 0 ? units[unitIndex] : '') + result;
        }
        
        number = Math.floor(number / 10000);
        unitIndex++;
    }
    
    return result;
}

// 숫자 포맷팅 함수
export function formatNumber(num, decimalPlaces = null) {
    try {
        if (num === undefined || num === null) return '0';
        if (Number.isInteger(num) === false) {
            if (decimalPlaces === null) {
                num = Math.round(num * 100) / 100;
            } else {
                num = Math.round(num * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces);
            }
        }
        return new Intl.NumberFormat('ko-KR').format(num);
    } catch (error) {
        console.error('formatNumber error:', error);
        return '0';
    }
}