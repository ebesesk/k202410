BEGIN_FUNCTION_MAP
	.Func,유렉스 주문가능 수량/금액 조회,CEXAQ21200,SERVICE=CEXAQ21200,headtype=B,CREATOR=이시종,CREDATE=2012/07/06 14:21:09;
	BEGIN_DATA_MAP
	CEXAQ21200InBlock1,In(*EMPTY*),input;
	begin
		레코드갯수, RecCnt, RecCnt, long, 5
		계좌번호, AcntNo, AcntNo, char, 20;
		비밀번호, Pwd, Pwd, char, 8;
		조회구분, QryTp, QryTp, char, 1;
		주문금액, OrdAmt, OrdAmt, long, 16;
		비율값, RatVal, RatVal, double, 19.8;
		선물옵션종목번호, FnoIsuNo, FnoIsuNo, char, 12;
		매매구분, BnsTpCode, BnsTpCode, char, 1;
		주문가, OrdPrc, OrdPrc, double, 13.2;
		유렉스가격조건구분코드, ErxPrcCndiTpCode, ErxPrcCndiTpCode, char, 1;
	end
	CEXAQ21200OutBlock1,In(*EMPTY*),output;
	begin
		레코드갯수, RecCnt, RecCnt, long, 5
		계좌번호, AcntNo, AcntNo, char, 20;
		비밀번호, Pwd, Pwd, char, 8;
		조회구분, QryTp, QryTp, char, 1;
		주문금액, OrdAmt, OrdAmt, long, 16;
		비율값, RatVal, RatVal, double, 19.8;
		선물옵션종목번호, FnoIsuNo, FnoIsuNo, char, 12;
		매매구분, BnsTpCode, BnsTpCode, char, 1;
		주문가, OrdPrc, OrdPrc, double, 13.2;
		유렉스가격조건구분코드, ErxPrcCndiTpCode, ErxPrcCndiTpCode, char, 1;
	end
	CEXAQ21200OutBlock2,Out(*EMPTY*),output;
	begin
		레코드갯수, RecCnt, RecCnt, long, 5
		계좌명, AcntNm, AcntNm, char, 40;
		조회일, QryDt, QryDt, char, 8;
		현재가, NowPrc, NowPrc, double, 15.2;
		주문가능수량, OrdAbleQty, OrdAbleQty, long, 16;
		신규주문가능수량, NewOrdAbleQty, NewOrdAbleQty, long, 16;
		청산주문가능수량, LqdtOrdAbleQty, LqdtOrdAbleQty, long, 16;
		사용예정증거금액, UsePreargMgn, UsePreargMgn, long, 16;
		사용예정현금증거금액, UsePreargMnyMgn, UsePreargMnyMgn, long, 16;
		주문가능금액, OrdAbleAmt, OrdAbleAmt, long, 16;
		현금주문가능금액, MnyOrdAbleAmt, MnyOrdAbleAmt, long, 16;
	end
	END_DATA_MAP
END_FUNCTION_MAP
