BEGIN_FUNCTION_MAP
	.Func,투자자매매종합(챠트),t1664,attr,block,headtype=A;
	BEGIN_DATA_MAP
	t1664InBlock,기본입력,input;
	begin
		시장구분,mgubun,mgubun,char,1;
		금액수량구분,vagubun,vagubun,char,1;
		시간일별구분,bdgubun,bdgubun,char,1;
		조회건수,cnt,cnt,int,3;
	end
	t1664OutBlock1,출력1,output,occurs;
	begin
		일자시간,dt,dt,char,8;
		증권순매수,tjj01,tjj01,double,12.0;
		보험순매수,tjj02,tjj02,double,12.0;
		투신순매수,tjj03,tjj03,double,12.0;
		은행순매수,tjj04,tjj04,double,12.0;
		종금순매수,tjj05,tjj05,double,12.0;
		기금순매수,tjj06,tjj06,double,12.0;
		기타순매수,tjj07,tjj07,double,12.0;
		개인순매수,tjj08,tjj08,double,12.0;
		외국인순매수,tjj17,tjj17,double,12.0;
		기관순매수,tjj18,tjj18,double,12.0;
		차익순매수,cha,cha,double,12.0;
		비차익순매수,bicha,bicha,double,12.0;
		종합순매수,totcha,totcha,double,12.0;
		베이시스,basis,basis,float,6.2;
	end
	END_DATA_MAP
END_FUNCTION_MAP

