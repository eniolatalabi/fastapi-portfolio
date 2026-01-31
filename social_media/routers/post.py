from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# Get ALL posts
# Returns the Post object joined with the number of votes
@router.get("", response_model=List[schemas.PostOut])
async def get_posts(
    db: Session = Depends(get_db), 
    limit: int = 10,       
    skip: int = 0,         
    search: Optional[str] = "" 
):
    # Selects the Post model and a count of votes
    # Joins the Vote table (Left Outer Join to include posts with 0 votes)
    # Groups by Post ID to aggregate the count
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
        .group_by(models.Post.id) \
        .filter(models.Post.title.contains(search)) \
        .limit(limit) \
        .offset(skip) \
        .all()
        
    return posts


# Create a NEW post
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# Get LATEST post
@router.get("/latest", response_model=schemas.PostOut)
def get_latest_post(db: Session = Depends(get_db)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
        .group_by(models.Post.id) \
        .order_by(models.Post.id.desc()) \
        .first()
        
    return post


# User gets all their OWN posts
@router.get("/myposts", response_model=List[schemas.PostOut])
async def get_my_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
        .group_by(models.Post.id) \
        .filter(models.Post.owner_id == current_user.id) \
        .all()
        
    return posts


# Get SINGLE post by ID
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
        .group_by(models.Post.id) \
        .filter(models.Post.id == id) \
        .first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
    return post


# DELETE post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    # Check if post exists
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist")
    
    # Check if the user owns the post
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# UPDATE post
@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    # Check if post exists
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
    
    # Check if the user owns the post
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform requested action")
    
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    
    return post_query.first()