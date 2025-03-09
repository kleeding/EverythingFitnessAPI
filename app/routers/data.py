from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2
from datetime import datetime
from .data_routers import weight

router = APIRouter(prefix="/data", tags=["Data"])

router.include_router(weight.router)

"""
 - get_datapoints
 - get_datapoint
 - create_datapoint
 - delete_datapoint
 - update_datapoint
"""

# , response_model=AllData | List[schemas.DataOut] | List[schemas.ExerciseOut]


@router.get("/")
def get_data(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    return {"message": "This will return all users datapoints."}
