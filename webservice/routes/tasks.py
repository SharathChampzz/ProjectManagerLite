from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from utils import auth, crud, dependencies
import schemas
import os
import logging
import requests

logger = logging.getLogger('app')
router = APIRouter()

from dotenv import load_dotenv
load_dotenv()
FTP_SERVER = os.getenv('FTP_SERVER')
print(f"FTP_SERVER: {FTP_SERVER}")

if not FTP_SERVER:
    raise ValueError('FTP_SERVER environment variable is not set.')

FTP_UPLOAD_URL = f"{FTP_SERVER}/upload/"
logger.info(f"FTP_UPLOAD_URL set to => {FTP_UPLOAD_URL}")

@router.get("/tasks/", dependencies=[Depends(auth.get_current_active_user)], response_model=list[schemas.Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    creator_name: str = None,
    assigner_name: str = None,
    subject_contains: str = None,
    criticality: str = None,
    status: str = None,
    thread_id: str = None,
    db: Session = Depends(dependencies.get_db)
):
    """Retrieve tasks with optional filtering."""
    filters = {}
    if creator_name:
        filters["creator_id"] = crud.get_user_by_username(db, creator_name).id
    if assigner_name:
        filters["assigner_id"] = crud.get_user_by_username(db, assigner_name).id
    if subject_contains:
        filters["subject__contains"] = subject_contains  # Adjust filter key
    if criticality:
        filters["criticality"] = criticality
    if status:
        filters["status"] = status
    if thread_id:
        filters["thread_id"] = thread_id

    tasks = crud.get_tasks(db, skip=skip, limit=limit, filters=filters)
    return tasks

@router.post("/tasks/", dependencies=[Depends(auth.get_current_active_user)], response_model=schemas.Task)
async def create_task(
    creator_name: str = Form(...),
    assigner_name: str = Form(...),
    subject: str = Form(...),
    criticality: schemas.TaskCriticality = Form(...),
    status: schemas.TaskStatus = Form(...),
    thread_id: str = Form(...),
    html_file: UploadFile = File(...),
    db: Session = Depends(dependencies.get_db)
):
    """Create a new task."""

    logger.info(f"Creating task with creator_name={creator_name}, assigner_name={assigner_name}, subject={subject}, criticality={criticality}, status={status}, thread_id={thread_id}, html_file={html_file.filename}")
    # Store the uploaded html file in FTP server
    file_location = html_file.filename
    with open(file_location, "wb+") as file_object:
        file_object.write(html_file.file.read())
        
    with open(file_location, "rb") as file:
        response = requests.post(FTP_UPLOAD_URL, files={"file": file})
        uploaded_path = response.json()['file_url']
        
    os.remove(file_location) # Remove the temp file from local storage

    # Validate the submitted data by mapping it to the schema
    task_data = schemas.TaskCreate(
        creator_name=creator_name,
        assigner_name=assigner_name,
        subject=subject,
        criticality=criticality,
        status=status,
        html_file=uploaded_path,
        thread_id=thread_id
    )
    
    # When Email processing is implemented, we should check if the creator and assigner exist in the database
    # If not, we should create them automatically
    # As we dont have existing users database, we will create them automatically to proceed with email processing
    if creator_name and not crud.check_user_exists(db, creator_name):
        create_dummy_user(db, creator_name)
        
    if assigner_name and not crud.check_user_exists(db, assigner_name):
        create_dummy_user(db, assigner_name)
    
    try:
        db_task = crud.create_task(db=db, task=task_data)
        return crud.get_task(db=db, task_id=db_task.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def create_dummy_user(db: Session, username: str):
    user = schemas.UserCreate(username=username, password="dummy")
    crud.create_user(db=db, user=user)

@router.get("/tasks/{task_id}", dependencies=[Depends(auth.get_current_active_user)], response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(dependencies.get_db)):
    """Retrieve a single task."""
    task = crud.get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", dependencies=[Depends(auth.get_current_active_user)], response_model=schemas.Task)
async def update_task(
    task_id: int,
    creator_name: str = Form(None ,description="Creator name"),
    assigner_name: str = Form(None, description="Assigner name"),
    subject: str = Form(None, description="Subject"),
    criticality: schemas.TaskCriticality = Form(None, description="Criticality"),
    status: schemas.TaskStatus = Form(None, description="Status"),
    html_file: UploadFile = File(None, description="HTML File"),
    thread_id: str = Form(None, description="Email Thread ID"),
    db: Session = Depends(dependencies.get_db)
):
    """Update a task."""
    # Save the uploaded file to the desired location
    if html_file:
        temp_file = html_file.filename
        with open(temp_file, "wb+") as file_object:
            file_object.write(html_file.file.read())
            
        with open(temp_file, "rb") as file:
            response = requests.post(FTP_UPLOAD_URL, files={"file": file})
            uploaded_path = response.json()['file_url']
            
        os.remove(temp_file) # Remove the temp file from local storage

    if creator_name and not crud.check_user_exists(db, creator_name):
        create_dummy_user(db, creator_name)
        
    if assigner_name and not crud.check_user_exists(db, assigner_name):
        create_dummy_user(db, assigner_name)
        
    task_data = schemas.TaskUpdate(
        creator_id=crud.get_user_by_username(db, creator_name).id if creator_name else None,
        assigner_id=crud.get_user_by_username(db, assigner_name).id if assigner_name else None,
        subject=subject,
        criticality=criticality,
        status=status,
        html_file=uploaded_path if html_file else None,
        thread_id=thread_id
    )
    
    db_task = crud.update_task(db=db, task_id=task_id, task=task_data)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return crud.get_task(db=db, task_id=task_id)

@router.delete("/tasks/{task_id}", dependencies=[Depends(auth.get_current_active_superuser)])
def delete_task(task_id: int, db: Session = Depends(dependencies.get_db)):
    """Delete a task."""
    result = crud.delete_task(db=db, task_id=task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}

# Commented out as downloading HTML files should be done via FTP server
# @router.get("/tasks/{task_id}/html", dependencies=[Depends(auth.get_current_active_user)])
# async def read_task_html(task_id: int, db: Session = Depends(dependencies.get_db)):
#     """Retrieve the HTML content of a task."""
#     task = crud.get_task(db=db, task_id=task_id)
#     if task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     if not os.path.isfile(task.html_file):
#         raise HTTPException(status_code=404, detail="File not found")
    
#     file_name = os.path.basename(task.html_file)
#     return FileResponse(task.html_file, media_type='application/octet-stream', filename=file_name)

# set last reminder sent time for a task
@router.post("/tasks/{task_id}/remindersent", dependencies=[Depends(auth.get_current_active_user)], response_model=schemas.Task)
def remind_task(task_id: int, db: Session = Depends(dependencies.get_db)):
    """Set the last reminder sent time for a task."""
    result = crud.set_last_reminder_sent_time(db=db, task_id=task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.get_task(db=db, task_id=task_id)
