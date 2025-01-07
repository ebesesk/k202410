from sqlalchemy import Column, String, Float, Integer
from app.db.base_class import Base

class ApartmentTransactionDB(Base):
    __tablename__ = "apt_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sggCd = Column(String(50), nullable=True)
    umdCd = Column(String(50), nullable=True)
    landCd = Column(String(50), nullable=True)
    bonbun = Column(String(50), nullable=True)
    bubun = Column(String(50), nullable=True)
    roadNm = Column(String(100), nullable=True)
    roadNmSggCd = Column(String(50), nullable=True)
    roadNmCd = Column(String(50), nullable=True)
    roadNmSeq = Column(String(50), nullable=True)
    roadNmbCd = Column(String(50), nullable=True)
    roadNmBonbun = Column(String(50), nullable=True)
    roadNmBubun = Column(String(50), nullable=True)
    umdNm = Column(String(100), nullable=True)
    aptNm = Column(String(100), nullable=True)
    jibun = Column(String(50), nullable=True)
    excluUseAr = Column(Float, nullable=True)
    dealYear = Column(String(4), nullable=True)
    dealMonth = Column(String(2), nullable=True)
    dealDay = Column(String(2), nullable=True)
    dealAmount = Column(String(50), nullable=True)
    floor = Column(String(10), nullable=True)
    buildYear = Column(String(4), nullable=True)
    aptSeq = Column(String(50), nullable=True)
    cdealType = Column(String(10), nullable=True)
    cdealDay = Column(String(20), nullable=True)
    dealingGbn = Column(String(20), nullable=True)
    estateAgentSggNm = Column(String(100), nullable=True)
    rgstDate = Column(String(20), nullable=True)
    aptDong = Column(String(50), nullable=True)
    slerGbn = Column(String(50), nullable=True)
    buyerGbn = Column(String(50), nullable=True)
    landLeaseholdGbn = Column(String(10), nullable=True)