BEGIN_FUNCTION_MAP
	.Func,신용거래동향(t1921),t1921,attr,block,headtype=A;
	BEGIN_DATA_MAP
	t1921InBlock,기본입력,input;
	begin
		종목코드,shcode,shcode,char,6;
		융자대주구분,gubun,gubun,char,1;
		날짜,date,date,char,8;
		IDX,idx,idx,long,4;
	end
	t1921OutBlock,출력,output;
	begin
		CNT,cnt,cnt,long,4;
		날짜,date,date,char,8;
		IDX,idx,idx,long,4;
	end
	t1921OutBlock1,출력1,output,occurs;
	begin
		날짜,mmdate,mmdate,char,8;
		종가,close,close,long,8;
		전일대비구분,sign,sign,char,1;
		전일대비,jchange,jchange,long,8;
		등락율,diff,diff,float,6.2;
		신규,nvolume,nvolume,long,8;
		상환,svolume,svolume,long,8;
		잔고,jvolume,jvolume,long,8;
		금액,price,price,long,8;
		대비,change,change,long,8;
		공여율,gyrate,gyrate,float,6.2;
		잔고율,jkrate,jkrate,float,6.2;
		종목코드,shcode,shcode,char,6;
	end
	END_DATA_MAP
END_FUNCTION_MAP

