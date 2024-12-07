from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
import database, schemas
import jwt
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse

# Secret key for JWT encoding/decoding
SECRET_KEY = "mysecretkey"  # Keep this secret!
ALGORITHM = "HS256"

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer instance to extract token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to verify the password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Helper function to create JWT token
def create_jwt_token(username: str):
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    payload = {
        "sub": username,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Dependency to extract user from JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/doc")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Login endpoint
@app.post("/login/")
def login(user: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(database.User).filter(database.User.username == user.username).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify the password
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create JWT token
    token = create_jwt_token(db_user.username)

    return {"access_token": token, "token_type": "bearer"}

# Example protected route
@app.get("/protected/")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}! This is a protected route."}

# Create a new coach
@app.post("/create_coach/")
def create_coach(coach: schemas.CoachCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(coach.password)
    db_coach = database.Coach(
        username=coach.username,
        hashed_password=hashed_password,
        location=coach.location,
        email=coach.email,
        role="coach",  # Explicitly set the role as 'coach'
    )
    db.add(db_coach)
    db.commit()
    db.refresh(db_coach)
    return db_coach

# Endpoint to place an schedule (requires authentication)
@app.post("/place_schedule/")
def place_schedule(schedule: schemas.ScheduleCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decode token and get the current user (coach)
    username = get_current_user(token)
    coach = db.query(database.Coach).filter(database.Coach.username == username).first()

    if not coach:
        raise HTTPException(status_code=400, detail="Coach not found")

    # Create a new schedule
    db_schedule = database.Schedule(
        coach_id=coach.id,  # Use coach.id from decoded token
        exercises=schedule.exercises,
        exercises_details=schedule.exercises_details,
        cost_per_hour=schedule.cost_per_hour
    )

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    return db_schedule

# Endpoint to get all schedules
@app.get("/get_schedules/")
def get_schedules(db: Session = Depends(get_db)):
    schedules = db.query(database.Schedule).all()
    return schedules

# Endpoint to get all coaches
@app.get("/get_all_coaches/")
def get_all_coaches(db: Session = Depends(get_db)):
    db_coaches = db.query(database.Coach).all()
    if not db_coaches:
        raise HTTPException(status_code=404, detail="No coaches found")
    return db_coaches

# Custom OpenAPI Schema to modify Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="This API uses JWT tokens for authentication. Obtain a token by sending a POST request to `/login/`. Use the format `Bearer <your-token>` in the Authorization header for authenticated endpoints.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Paste your token in the format 'Bearer <your-token>' to authenticate."
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "security" in method:
                method["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
