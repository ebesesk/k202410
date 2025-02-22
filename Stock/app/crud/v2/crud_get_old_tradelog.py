from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func, and_, cast, Float, JSON, text
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.models.investment_models import (Transaction, 
                                          Position, 
                                          Portfolio, 
                                          Account,
                                          Asset)
from app.schemas import investment_schemas_v2 as schemas
from app.crud.v2 import crud_cash_balance as crud_cash_balance

from app.utils.utils import get_current_kst_time, convert_to_kst
from app.crud.v2 import crud_position_transaction as crud_position
from app.crud.v2 import crud_account as crud_account
from app.crud.v2 import crud_asset as crud_asset

from app.crud import stock as crud_stock
from app.utils.utils import get_investment_db, get_db

