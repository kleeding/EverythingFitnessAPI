from datetime import datetime
from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from ...database import get_db
from ... import models, schemas, oauth2

router = APIRouter(prefix="/weight")


@router.get("/", response_model=List[schemas.DataOut])
def get_weights(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
    limit: int = 10,
    offset: int = 0,
):
    data_query = db.query(models.Weight).filter(
        models.Weight.owner_id == current_user.id
    )

    data_query = data_query.limit(limit).offset(offset)
    data = data_query.all()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No weight data with the given criteria found.",
        )

    return data


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.DataEntry)
def add_weight(
    weight: schemas.DataEntry,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    data = (
        db.query(models.Weight)
        .filter(
            and_(
                models.Weight.owner_id == current_user.id,
                models.Weight.date == weight.date,
            )
        )
        .first()
    )
    if data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Weight already record for date: {weight.date}",
        )

    new_weight = models.Weight(owner_id=current_user.id, **weight.model_dump())
    db.add(new_weight)
    db.commit()
    db.refresh(new_weight)

    return new_weight


@router.get("/{date}", response_model=schemas.DataEntry)
def get_weight(
    date: datetime,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    date = date.strftime("%Y-%m-%d")
    data = (
        db.query(models.Weight)
        .filter(
            and_(models.Weight.owner_id == current_user.id, models.Weight.date == date)
        )
        .first()
    )

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Weight data with date: {date} was not found",
        )

    return data


@router.delete("/{date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weight(
    date: datetime,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    date = date.strftime("%Y-%m-%d")

    data_query = db.query(models.Weight).filter(
        and_(models.Weight.owner_id == current_user.id, models.Weight.date == date)
    )
    data = data_query.first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No weight record exists for date: {date}.",
        )

    data_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{date}", response_model=schemas.DataOut)
def update_weight(
    date: datetime,
    updated_weight: schemas.DataBase,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    date = date.strftime("%Y-%m-%d")

    data_query = db.query(models.Weight).filter(
        and_(models.Weight.owner_id == current_user.id, models.Weight.date == date)
    )
    data = data_query.first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No weight record exists for date: {date}.",
        )

    data_query.update(updated_weight.model_dump(), synchronize_session=False)
    db.commit()

    return data_query.first()
