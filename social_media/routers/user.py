from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash_password(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        # Unique constraint on email: surface a clean conflict instead
        # of a 500.
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="A user with this email already exists")
    db.refresh(new_user)
    return new_user


# The /me routes are registered before /{id} so the literal path wins
# route matching. They take no id parameter by design: with no way to
# address another account, there is no object-level authorization
# surface to defend.
@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_profile(
        current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_current_user(
        updates: schemas.UserUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(oauth2.get_current_user)):
    if updates.email is not None:
        current_user.email = updates.email
    if updates.phone_number is not None:
        current_user.phone_number = updates.phone_number
    if updates.password is not None:
        current_user.password = utils.hash_password(updates.password)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="A user with this email already exists")
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(oauth2.get_current_user)):
    # Posts and votes cascade via the foreign keys' ondelete rules.
    db.delete(current_user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")
    return user
