BEGIN_FUNCTION_MAP
	.Func,�ɼ�������(t2301),t2301,attr,block,headtype=A;
	BEGIN_DATA_MAP
	t2301InBlock,�⺻�Է�,input;
	begin
		����,yyyymm,yyyymm,char,6;
		�̴ϱ���(M:�̴�G:����),gubun,gubun,char,1;
	end
	t2301OutBlock,���,output;
	begin
		������������,histimpv,histimpv,long,4;
		�ɼ�������,jandatecnt,jandatecnt,long,4;
		�ݿɼǴ�ǥIV,cimpv,cimpv,float,6.3;
		ǲ�ɼǴ�ǥIV,pimpv,pimpv,float,6.3;
		�ٿ������簡,gmprice,gmprice,float,6.2;
		�ٿ������ϴ�񱸺�,gmsign,gmsign,char,1;
		�ٿ������ϴ��,gmchange,gmchange,float,6.2;
		�ٿ��������,gmdiff,gmdiff,float,6.2;
		�ٿ����ŷ���,gmvolume,gmvolume,long,12;
		�ٿ��������ڵ�,gmshcode,gmshcode,char,8;
	end
	t2301OutBlock1,���1,output,occurs;
	begin
		��簡,actprice,actprice,float,6.2;
		�ݿɼ��ڵ�,optcode,optcode,char,8;
		���簡,price,price,float,6.2;
		���ϴ�񱸺�,sign,sign,char,1;
		���ϴ��,change,change,float,6.2;
		�����,diff,diff,float,6.2;
		�ŷ���,volume,volume,long,12;
		IV,iv,iv,float,6.2;
		�̰�������,mgjv,mgjv,long,12;
		�̰�����������,mgjvupdn,mgjvupdn,long,12;
		�ŵ�ȣ��,offerho1,offerho1,float,6.2;
		�ż�ȣ��,bidho1,bidho1,float,6.2;
		ü�ᷮ,cvolume,cvolume,long,12;
		��Ÿ,delt,delt,float,6.4;
		����,gama,gama,float,6.4;
		����,vega,vega,float,6.4;
		��Ÿ,ceta,ceta,float,6.4;
		�ο�,rhox,rhox,float,6.4;
		�̷а�,theoryprice,theoryprice,float,6.2;
		���簡ġ,impv,impv,float,6.2;
		�ð���ġ,timevl,timevl,float,6.2;
		�ܰ�����,jvolume,jvolume,long,12;
		�򰡼���,parpl,parpl,long,12;
		û�갡�ɼ���,jngo,jngo,long,6;
		�ŵ��ܷ�,offerrem1,offerrem1,long,12;
		�ż��ܷ�,bidrem1,bidrem1,long,12;
		�ð�,open,open,float,6.2;
		����,high,high,float,6.2;
		����,low,low,float,6.2;
		ATM����,atmgubun,atmgubun,char,1;
		����ȯ��,jisuconv,jisuconv,float,6.2;
		�ŷ����,value,value,float,12;
	end
	t2301OutBlock2,���2,output,occurs;
	begin
		��簡,actprice,actprice,float,6.2;
		ǲ�ɼ��ڵ�,optcode,optcode,char,8;
		���簡,price,price,float,6.2;
		���ϴ�񱸺�,sign,sign,char,1;
		���ϴ��,change,change,float,6.2;
		�����,diff,diff,float,6.2;
		�ŷ���,volume,volume,long,12;
		IV,iv,iv,float,6.2;
		�̰�������,mgjv,mgjv,long,12;
		�̰�����������,mgjvupdn,mgjvupdn,long,12;
		�ŵ�ȣ��,offerho1,offerho1,float,6.2;
		�ż�ȣ��,bidho1,bidho1,float,6.2;
		ü�ᷮ,cvolume,cvolume,long,12;
		��Ÿ,delt,delt,float,6.4;
		����,gama,gama,float,6.4;
		����,vega,vega,float,6.4;
		��Ÿ,ceta,ceta,float,6.4;
		�ο�,rhox,rhox,float,6.4;
		�̷а�,theoryprice,theoryprice,float,6.2;
		���簡ġ,impv,impv,float,6.2;
		�ð���ġ,timevl,timevl,float,6.2;
		�ܰ�����,jvolume,jvolume,long,12;
		�򰡼���,parpl,parpl,long,12;
		û�갡�ɼ���,jngo,jngo,long,6;
		�ŵ��ܷ�,offerrem1,offerrem1,long,12;
		�ż��ܷ�,bidrem1,bidrem1,long,12;
		�ð�,open,open,float,6.2;
		����,high,high,float,6.2;
		����,low,low,float,6.2;
		ATM����,atmgubun,atmgubun,char,1;
		����ȯ��,jisuconv,jisuconv,float,6.2;
		�ŷ����,value,value,float,12;
	end
	END_DATA_MAP
END_FUNCTION_MAP
