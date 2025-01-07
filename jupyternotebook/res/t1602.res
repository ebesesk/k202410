BEGIN_FUNCTION_MAP
	.Func,시간대별투자자매매추이(t1602),t1602,attr,block,headtype=A;
	BEGIN_DATA_MAP
	t1602InBlock,기본입력,input;
	begin
		시장구분,market,market,char,1;
		업종코드,upcode,upcode,char,3;
		수량구분,gubun1,gubun1,char,1;
		전일분구분,gubun2,gubun2,char,1;
		CTSTIME,cts_time,cts_time,char,8;
		CTSIDX,cts_idx,cts_idx,long,4;
		조회건수,cnt,cnt,int,4;
		직전대비구분(C:직전대비),gubun3,gubun3,char,1;
	end
	t1602OutBlock,기본출력,output;
	begin
		CTSTIME,cts_time,cts_time,char,8;
		개인투자자코드,tjjcode_08,tjjcode_08,char,4;
		개인매수,ms_08,ms_08,long,12;
		개인매도,md_08,md_08,long,12;
		개인증감,rate_08,rate_08,long,12;
		개인순매수,svolume_08,svolume_08,long,12;
		외국인투자자코드,jjcode_17,tjjcode_17,char,4;
		외국인매수,ms_17,ms_17,long,12;
		외국인매도,md_17,md_17,long,12;
		외국인증감,rate_17,rate_17,long,12;
		외국인순매수,svolume_17,svolume_17,long,12;
		기관계투자자코드,jjcode_18,tjjcode_18,char,4;
		기관계매수,ms_18,ms_18,long,12;
		기관계매도,md_18,md_18,long,12;
		기관계증감,rate_18,rate_18,long,12;
		기관계순매수,svolume_18,svolume_18,long,12;
		증권투자자코드,jjcode_01,tjjcode_01,char,4;
		증권매수,ms_01,ms_01,long,12;
		증권매도,md_01,md_01,long,12;
		증권증감,rate_01,rate_01,long,12;
		증권순매수,svolume_01,svolume_01,long,12;
		투신투자자코드,jjcode_03,tjjcode_03,char,4;
		투신매수,ms_03,ms_03,long,12;
		투신매도,md_03,md_03,long,12;
		투신증감,rate_03,rate_03,long,12;
		투신순매수,svolume_03,svolume_03,long,12;
		은행투자자코드,jjcode_04,tjjcode_04,char,4;
		은행매수,ms_04,ms_04,long,12;
		은행매도,md_04,md_04,long,12;
		은행증감,rate_04,rate_04,long,12;
		은행순매수,svolume_04,svolume_04,long,12;
		보험투자자코드,jjcode_02,tjjcode_02,char,4;
		보험매수,ms_02,ms_02,long,12;
		보험매도,md_02,md_02,long,12;
		보험증감,rate_02,rate_02,long,12;
		보험순매수,svolume_02,svolume_02,long,12;
		종금투자자코드,jjcode_05,tjjcode_05,char,4;
		종금매수,ms_05,ms_05,long,12;
		종금매도,md_05,md_05,long,12;
		종금증감,rate_05,rate_05,long,12;
		종금순매수,svolume_05,svolume_05,long,12;
		기금투자자코드,jjcode_06,tjjcode_06,char,4;
		기금매수,ms_06,ms_06,long,12;
		기금매도,md_06,md_06,long,12;
		기금증감,rate_06,rate_06,long,12;
		기금순매수,svolume_06,svolume_06,long,12;
		기타투자자코드,jjcode_07,tjjcode_07,char,4;
		기타매수,ms_07,ms_07,long,12;
		기타매도,md_07,md_07,long,12;
		기타증감,rate_07,rate_07,long,12;
		기타순매수,svolume_07,svolume_07,long,12;
		국가투자자코드,jjcode_11,tjjcode_11,char,4;
		국가매수,ms_11,ms_11,long,12;
		국가매도,md_11,md_11,long,12;
		국가증감,rate_11,rate_11,long,12;
		국가순매수,svolume_11,svolume_11,long,12;
		사모펀드코드,jjcode_00,tjjcode_00,char,4;
		사모펀드매수,ms_00,ms_00,long,12;
		사모펀드매도,md_00,md_00,long,12;
		사모펀드증감,rate_00,rate_00,long,12;
		사모펀드순매수,svolume_00,svolume_00,long,12;
	end
	t1602OutBlock1,출력1,output,occurs;
	begin
		시간,time,time,char,8;
		개인순매수,sv_08,sv_08,long,12;
		외국인순매수,sv_17,sv_17,long,12;
		기관계순매수,sv_18,sv_18,long,12;
		증권순매수,sv_01,sv_01,long,12;
		투신순매수,sv_03,sv_03,long,12;
		은행순매수,sv_04,sv_04,long,12;
		보험순매수,sv_02,sv_02,long,12;
		종금순매수,sv_05,sv_05,long,12;
		기금순매수,sv_06,sv_06,long,12;
		기타순매수,sv_07,sv_07,long,12;
		국가순매수,sv_11,sv_11,long,12;
		사모펀드순매수,sv_00,sv_00,long,12;
	end
	END_DATA_MAP
END_FUNCTION_MAP

