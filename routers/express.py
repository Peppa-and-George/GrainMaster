from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Query, status, Body, HTTPException
from fastapi.responses import JSONResponse

from schema.tables import Express, LogisticsPlan
from schema.common import page_with_order
from schema.database import SessionLocal
from models.base import WarehouseSchema

warehouse_router = APIRouter()
