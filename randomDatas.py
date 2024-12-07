from database import engine, Coach, Schedule

rwanda_districts = [
    "Nyarugenge", "Gasabo", "Kicukiro",  # City of Kigali
    "Burera", "Gakenke", "Gicumbi", "Musanze", "Rulindo",  # Northern Province
    "Gisagara", "Huye", "Kamonyi", "Muhanga", "Nyamagabe", "Nyanza", "Nyaruguru", "Ruhango",  # Southern Province
    "Bugesera", "Gatsibo", "Kayonza", "Kirehe", "Ngoma", "Nyagatare", "Rwamagana",  # Eastern Province
    "Karongi", "Ngororero", "Nyabihu", "Nyamasheke", "Rubavu", "Rusizi", "Rutsiro"  # Western Province
]

exercises_items = [
    {"exercises": "Push-Ups", "exercises_details": "Bodyweight exercise to strengthen the chest, shoulders, and triceps", "cost_per_hour": 0},
    {"exercises": "Squats", "exercises_details": "Lower body exercise to build strength in the legs and glutes", "cost_per_hour": 0},
    {"exercises": "Yoga", "exercises_details": "Mind and body practice to improve flexibility and reduce stress", "cost_per_hour": 2000},
]


coaches = [
    {"username": "john_doe1", "email": "john_doe1@example.com"},
    {"username": "jane_smith2", "email": "jane_smith2@example.com"},
    {"username": "paul_brown3", "email": "paul_brown3@example.com"},
    {"username": "emily_davis4", "email": "emily_davis4@example.com"},
    {"username": "michael_jones5", "email": "michael_jones5@example.com"},
    {"username": "sarah_miller6", "email": "sarah_miller6@example.com"},
    {"username": "david_wilson7", "email": "david_wilson7@example.com"},
    {"username": "linda_moore8", "email": "linda_moore8@example.com"},
    {"username": "robert_taylor9", "email": "robert_taylor9@example.com"},
    {"username": "nancy_white10", "email": "nancy_white10@example.com"},
    {"username": "joshua_hall11", "email": "joshua_hall11@example.com"},
    {"username": "amanda_lewis12", "email": "amanda_lewis12@example.com"},
    {"username": "daniel_clark13", "email": "daniel_clark13@example.com"},
    {"username": "laura_robinson14", "email": "laura_robinson14@example.com"},
    {"username": "mark_harris15", "email": "mark_harris15@example.com"},
    {"username": "elizabeth_thomas16", "email": "elizabeth_thomas16@example.com"},
    {"username": "kevin_scott17", "email": "kevin_scott17@example.com"},
    {"username": "patricia_adams18", "email": "patricia_adams18@example.com"},
    {"username": "charles_evans19", "email": "charles_evans19@example.com"},
    {"username": "rebecca_martin20", "email": "rebecca_martin20@example.com"},
    {"username": "james_roberts21", "email": "james_roberts21@example.com"},
    {"username": "karen_mitchell22", "email": "karen_mitchell22@example.com"},
    {"username": "steven_carter23", "email": "steven_carter23@example.com"},
    {"username": "carolyn_wright24", "email": "carolyn_wright24@example.com"},
    {"username": "anthony_turner25", "email": "anthony_turner25@example.com"},
    {"username": "deborah_parker26", "email": "deborah_parker26@example.com"},
    {"username": "matthew_cooper27", "email": "matthew_cooper27@example.com"},
    {"username": "susan_anderson28", "email": "susan_anderson28@example.com"},
    {"username": "andrew_nguyen29", "email": "andrew_nguyen29@example.com"},
    {"username": "anna_hughes30", "email": "anna_hughes30@example.com"},
    {"username": "peter_king31", "email": "peter_king31@example.com"},
    {"username": "diane_bell32", "email": "diane_bell32@example.com"},
    {"username": "chris_wood33", "email": "chris_wood33@example.com"},
    {"username": "melissa_price34", "email": "melissa_price34@example.com"},
    {"username": "thomas_baker35", "email": "thomas_baker35@example.com"}
]


import random
from sqlalchemy.orm import Session
# from passlib.context import CryptContext


# Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database session
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

# Generate 5000 unique coaches and 11405 schedules
def populate_data():
    db = next(get_db())

    try:
        # Generate 5000 unique coaches
        coaches = []
        for i in range(500):
            username = f"user_{i+1}"
            email = f"user_{i+1}@example.com"
            location = random.choice(rwanda_districts)
            password = f"password_{i+1}"
            hashed_password = password
            # pwd_context.hash(password)

            coach = Coach(
                username=username,
                email=email,
                location=location,
                hashed_password=hashed_password,
            )
            coaches.append(coach)
            print(coach.email)

        db.add_all(coaches)
        db.commit()

        # Fetch all coaches from the database
        all_coaches = db.query(Coach).all()

        # Generate 11405 schedules
        schedules = []
        for _ in range(500000):
            coach = random.choice(all_coaches)
            exercises = random.choice(exercises_items)

            schedule = Schedule(
                coach_id=coach.id,
                exercises=exercises["exercises"],
                exercises_details=exercises["exercises_details"],
                cost_per_hour=exercises["cost_per_hour"],
            )
            schedules.append(schedule)
            print(schedule.exercises)

        db.add_all(schedules)
        db.commit()

        print("Data populated successfully!")
    except Exception as e:
        db.rollback()
        print("An error occurred:", e)
    finally:
        db.close()

# Run the script
if __name__ == "__main__":
    populate_data()
