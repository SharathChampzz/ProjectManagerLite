from fastapi import APIRouter, Depends, HTTPException
from utils import auth, crud, dependencies
import schemas
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)) -> schemas.User:
    """Create a new user."""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)) -> schemas.User:
    """Retrieve the current user."""
    return current_user

@router.get('/', response_model=list[schemas.User], dependencies=[Depends(auth.get_current_active_user)])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)) -> list[schemas.User]:
    """Get a list of users from the database."""
    return crud.get_users(db, skip=skip, limit=limit)

@router.get('/{user_id}', response_model=schemas.User, dependencies=[Depends(auth.get_current_active_user)])
def get_user(user_id: int, db: Session = Depends(dependencies.get_db)) -> schemas.User:
    """Get a user by their ID."""
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put('/{user_id}', response_model=schemas.User, dependencies=[Depends(auth.get_current_active_superuser)])
def update_user(user_id: int, user: schemas.UpdateUser, db: Session = Depends(dependencies.get_db)) -> schemas.User:
    """Update a user in the database."""
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user=user)

@router.delete('/{user_id}', dependencies=[Depends(auth.get_current_active_superuser)])
def delete_user(user_id: int, db: Session = Depends(dependencies.get_db)) -> dict:
    """Delete a user from the database."""
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = crud.update_user(db=db, user_id=user_id, user=schemas.UpdateUser(is_active=False))
    # result = crud.delete_user(db=db, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deletion is not supported. Successfully disabled the user instead."}

@router.get("/me/items")
async def read_own_items(current_user: schemas.User = Depends(auth.get_current_active_user)) -> dict:
    """Retrieve items owned by the current user."""
    return [{"item_id": "Foo", "owner": current_user.username}]