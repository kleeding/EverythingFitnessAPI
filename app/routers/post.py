from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.Post])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    search: str | None = None,
    id: int | None = None,
    limit: int = 10,
    offset: int = 0,
):
    print(id)
    post_query = db.query(models.Post)

    if search:
        post_query = post_query.filter(models.Post.title.contains(search))

    if not id:
        post_query = post_query.filter(
            or_(models.Post.owner_id == current_user.id, models.Post.private == False)
        )
    else:
        if id == current_user.id:
            post_query = post_query.filter(models.Post.owner_id == id)
        post_query = post_query.filter(models.Post.private == False)

    post_query = post_query.limit(limit).offset(offset)
    posts = post_query.all()

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.PostBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    return {"data": "This will create a post"}


@router.get("/{id}")
def get_post(id: int):
    return {"data": f"This will return the post with id: {id}"}


@router.delete("/{id}")
def delete_post():
    pass


@router.put("/{id}")
def update_post():
    pass
