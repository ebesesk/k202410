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