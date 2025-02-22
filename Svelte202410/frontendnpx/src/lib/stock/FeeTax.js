export function calculateFeeTax(assetCategory, code, action, amount) {
    const COMMISSION_RATE_STOCK_KR = 0.00015;  // 증권 수수료
    const COMMISSION_RATE_STOCK_US = 0.0025;  // 해외 수수료
    const TAX_RATE_STOCK_KR = 0.0015;  // 증권 세금
    const INTERNATIONAL_TRANSACTION_FEES = 0.00003;  // 해외 주식 수수료
    const DIVIDEND_TAX_RATE_STOCK_KR = 0.154;  // 배당 소득세
    const DIVIDEND_TAX_RATE_STOCK_US = 0.15;  // 배당 소득세
    let fee = null;
    let tax = null;

    // 소문자로 변환
    action = action.toLowerCase();
    assetCategory = assetCategory.toLowerCase();
    code = code.toLowerCase();
    if (action === 'in' && assetCategory.includes('dividend')) {
        if (assetCategory.includes("krw")) {
            tax = Math.abs(Math.trunc(amount * DIVIDEND_TAX_RATE_STOCK_KR)) * -1;
            amount = Math.abs(amount);
        }else if (assetCategory.includes("usd")) {
            tax = Math.abs(Math.round(100 * amount * DIVIDEND_TAX_RATE_STOCK_US) / 100) * -1;
            amount = Math.abs(amount);
        }
        return {
            fee: 0,
            tax: tax
        }
    }
    if (!assetCategory.startsWith('cash') && !assetCategory.startsWith('exchange')) {
        if (action === 'in' && assetCategory.includes('krw')) {
            fee = Math.abs(Math.trunc(amount * COMMISSION_RATE_STOCK_KR)) * -1 ;
            tax = 0;
        }else if (action === 'out' && assetCategory.includes('krw')) {
            fee = Math.abs(Math.trunc(amount * COMMISSION_RATE_STOCK_KR)) * -1;
            tax = Math.abs(Math.trunc(amount * TAX_RATE_STOCK_KR)) * -1;
        }
        if (action === 'in' && assetCategory.includes('usd')) {
            fee = Math.abs(Math.round(100 * amount * COMMISSION_RATE_STOCK_US) / 100) * -1;
            tax = 0;
        }else if (action === 'out' && assetCategory.includes('usd')) {
            fee = Math.abs(Math.round(100 * amount * COMMISSION_RATE_STOCK_US) / 100) * -1;
            tax = Math.abs(Math.round(100 * amount * INTERNATIONAL_TRANSACTION_FEES) / 100) * -1;
        }
    }

    if (assetCategory.startsWith('exchange')) {
        if (action === 'in') {
            fee = 0;
            tax = 0;
        }
    }
    console.log('assetCategory:', assetCategory);
    console.log('action:', action);
    console.log('amount:', amount);
    console.log('fee:', fee);
    console.log('tax:', tax);
    return {
        fee: fee,
        tax: tax
    }
}