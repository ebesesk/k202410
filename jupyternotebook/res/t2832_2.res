BEGIN_FUNCTION_MAP
	.Func,EUREX야간옵션선물시간대별체결조회(t2832),t2832,attr,block,headtype=A;
	BEGIN_DATA_MAP
	t2832InBlock,기본입력,input;
	begin
		단축코드,focode,focode,char,8;
		특이거래량,cvolume,cvolume,long,12;
		시작시간,stime,stime,char,4;
		종료시간,etime,etime,char,4;
		시간CTS,cts_time,cts_time,char,10;
	end
	t2832OutBlock,출력,output;
	begin
		시간CTS,cts_time,cts_time,char,10;
	end
	t2832OutBlock1,출력1,output,occurs;
	begin
		시간,chetime,chetime,char,10;
		현재가,price,price,float,6.2;
		전일대비구분,sign,sign,char,1;
		전일대비,change,change,float,6.2;
		체결수량,cvolume,cvolume,long,8;
		체결강도,chdegree,chdegree,float,8.2;
		매도호가,offerho,offerho,float,6.2;
		매수호가,bidho,bidho,float,6.2;
		거래량,volume,volume,double,12.0;
		누적매수체결량,n_msvolume,n_msvolume,double,12.0;
		누적매도체결량,n_mdvolume,n_mdvolume,double,12.0;
		누적순매수체결량,s_msvolume,s_msvolume,double,12.0;
		누적매수체결건수,n_mschecnt,n_mschecnt,long,8;
		누적매도체결건수,n_mdchecnt,n_mdchecnt,long,8;
		누적순매수체결건수,s_mschecnt,s_mschecnt,long,8;
	end
	END_DATA_MAP
END_FUNCTION_MAP

