BEGIN_FUNCTION_MAP
	.Func,주식당일매매일지/수수료(전일)(t0151),t0151,tuxcode=t0151, headtype=C;
	BEGIN_DATA_MAP
	t0151InBlock,기본입력,input;
	begin
		일자,date,date,char,8;
		계좌번호,accno,accno,char,11;
		CTS_매매구분,cts_medosu,cts_medosu,char,1;
		CTS_종목번호,cts_expcode,cts_expcode,char,12;
		CTS_단가,cts_price,cts_price,char,9;
		CTS_매체,cts_middiv,cts_middiv,char,2;
	end
	t0151OutBlock,출력,output;
	begin
		매도수량,mdqty,mdqty,long,9;
		매도약정금액,mdamt,mdamt,long,18;
		매도수수료,mdfee,mdfee,long,18;
		매도거래세,mdtax,mdtax,long,18;
		매도농특세,mdargtax,mdargtax,long,18;
		매도제비용합,tmdtax,tmdtax,long,18;
		매도정산금액,mdadjamt,mdadjamt,long,18;
		매수수량,msqty,msqty,long,9;
		매수약정금액,msamt,msamt,long,18;
		매수수수료,msfee,msfee,long,18;
		매수제비용합,tmstax,tmstax,long,18;
		매수정산금액,msadjamt,msadjamt,long,18;
		합계수량,tqty,tqty,long,9;
		합계약정금액,tamt,tamt,long,18;
		합계수수료,tfee,tfee,long,18;
		합계거래세,tottax,tottax,long,18;
		합계농특세,targtax,targtax,long,18;
		합계제비용합,ttax,ttax,long,18;
		합계정산금액,tadjamt,tadjamt,long,18;
		CTS_매매구분,cts_medosu,cts_medosu,char,1;
		CTS_종목번호,cts_expcode,cts_expcode,char,12;
		CTS_단가,cts_price,cts_price,char,9;
		CTS_매체,cts_middiv,cts_middiv,char,2;
	end
	t0151OutBlock1,출력1,output,occurs;
	begin
		매매구분,medosu,medosu,char,10;
		종목번호,expcode,expcode,char,12;
		수량,qty,qty,long,9;
		단가,price,price,long,9;
		약정금액,amt,amt,long,18;
		수수료,fee,fee,long,18;
		거래세,tax,tax,long,18;
		농특세,argtax,argtax,long,18;
		정산금액,adjamt,adjamt,long,18;
		매체,middiv,middiv,char,20;
	end
	END_DATA_MAP
END_FUNCTION_MAP

