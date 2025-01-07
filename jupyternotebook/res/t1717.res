BEGIN_FUNCTION_MAP
	.Func,외인기관종목별동향(t1717),t1717,attr,block,headtype=A;
	BEGIN_DATA_MAP
	t1717InBlock,기본입력,input;
	begin
		종목코드,shcode,shcode,char,6;
		구분(0:일간순매수1:기간누적순매수),gubun,gubun,char,1;
		시작일자(일간조회일경우는space),fromdt,fromdt,char,8;
		종료일자,todt,todt,char,8;
	end
	t1717OutBlock,출력,output,occurs;
	begin
		일자,date,date,char,8;
		종가,close,close,long,8;
		전일대비구분,sign,sign,char,1;
		전일대비,change,change,long,8;
		등락율,diff,diff,float,6.2;
		누적거래량,volume,volume,long,12;
		사모펀드(순매수량),tjj0000_vol,tjj0000_vol,long,12;
		증권(순매수량),tjj0001_vol,tjj0001_vol,long,12;
		보험(순매수량),tjj0002_vol,tjj0002_vol,long,12;
		투신(순매수량),tjj0003_vol,tjj0003_vol,long,12;
		은행(순매수량),tjj0004_vol,tjj0004_vol,long,12;
		종금(순매수량),tjj0005_vol,tjj0005_vol,long,12;
		기금(순매수량),tjj0006_vol,tjj0006_vol,long,12;
		기타법인(순매수량),tjj0007_vol,tjj0007_vol,long,12;
		개인(순매수량),tjj0008_vol,tjj0008_vol,long,12;
		등록외국인(순매수량),tjj0009_vol,tjj0009_vol,long,12;
		미등록외국인(순매수량),tjj0010_vol,tjj0010_vol,long,12;
		국가외(순매수량),tjj0011_vol,tjj0011_vol,long,12;
		기관(순매수량),tjj0018_vol,tjj0018_vol,long,12;
		외인계(순매수량)(등록+미등록),tjj0016_vol,tjj0016_vol,long,12;
		기타계(순매수량)(기타+국가),tjj0017_vol,tjj0017_vol,long,12;
		사모펀드(단가),tjj0000_dan,tjj0000_dan,long,12;
		증권(단가),tjj0001_dan,tjj0001_dan,long,12;
		보험(단가),tjj0002_dan,tjj0002_dan,long,12;
		투신(단가),tjj0003_dan,tjj0003_dan,long,12;
		은행(단가),tjj0004_dan,tjj0004_dan,long,12;
		종금(단가),tjj0005_dan,tjj0005_dan,long,12;
		기금(단가),tjj0006_dan,tjj0006_dan,long,12;
		기타법인(단가),tjj0007_dan,tjj0007_dan,long,12;
		개인(단가),tjj0008_dan,tjj0008_dan,long,12;
		등록외국인(단가),tjj0009_dan,tjj0009_dan,long,12;
		미등록외국인(단가),tjj0010_dan,tjj0010_dan,long,12;
		국가외(단가),tjj0011_dan,tjj0011_dan,long,12;
		기관(단가),tjj0018_dan,tjj0018_dan,long,12;
		외인계(단가)(등록+미등록),tjj0016_dan,tjj0016_dan,long,12;
		기타계(단가)(기타+국가),tjj0017_dan,tjj0017_dan,long,12;
	end
	END_DATA_MAP
END_FUNCTION_MAP

