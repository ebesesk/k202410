BEGIN_FUNCTION_MAP
	.Func,과거데이터시간대별조회(t8427),t8427,attr,block,headtype=A;
	BEGIN_DATA_MAP
	t8427InBlock,기본입력,input;
	begin
		선물옵션구분,fo_gbn,fo_gbn,char,1;
		조회년도,yyyy,yyyy,char,4;
		조회월,mm,mm,char,2;
		옵션콜풋구분,cp_gbn,cp_gbn,char,1;
		옵션행사가,actprice,actprice,float,6.2;
		선물옵션코드,focode,focode,char,8;
		일분구분,dt_gbn,dt_gbn,char,1;
		분간격,min_term,min_term,char,2;
		날짜,date,date,char,8;
		시간,time,time,char,6;
	end
	t8427OutBlock,출력,output;
	begin
		선물옵션코드,focode,focode,char,8;
		날짜,date,date,char,8;
		시간,time,time,char,6;
	end
	t8427OutBlock1,출력1,output,occurs;
	begin
		날짜,date,date,char,8;
		시간,time,time,char,6;
		시가,open,open,float,6.2;
		고가,high,high,float,6.2;
		저가,low,low,float,6.2;
		종가,close,close,float,6.2;
		전일대비구분,sign,sign,char,1;
		전일대비,change,change,float,6.2;
		등락율,diff,diff,float,6.2;
		거래량,volume,volume,long,12;
		거래증가율,diff_vol,diff_vol,float,10.2;
		미결수량,openyak,openyak,long,8;
		미결증감,openyakupdn,openyakupdn,long,8;
		거래대금,value,value,float,12;
	end
	END_DATA_MAP
END_FUNCTION_MAP

