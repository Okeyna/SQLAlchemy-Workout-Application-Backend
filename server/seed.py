from app import app
from models import db, Exercise, Workout, WorkoutExercise
from datetime import date, timedelta
import random

def seed():
    with app.app_context():
        # Clear existing data (optional)
        db.drop_all()
        db.create_all()

        # Create exercises
        exercises = [
            Exercise(name="Push-up", category="Strength", equipment_needed=False),
            Exercise(name="Squat", category="Strength", equipment_needed=False),
            Exercise(name="Deadlift", category="Strength", equipment_needed=True),
            Exercise(name="Plank", category="Core", equipment_needed=False),
            Exercise(name="Pull-up", category="Strength", equipment_needed=True),
            Exercise(name="Burpee", category="Cardio", equipment_needed=False),
            Exercise(name="Lunges", category="Strength", equipment_needed=False),
            Exercise(name="Bicep Curl", category="Strength", equipment_needed=True),
        ]
        db.session.add_all(exercises)
        db.session.commit()

        # Create workouts
        today = date.today()
        workouts = [
            Workout(date=today - timedelta(days=2), duration_minutes=45, notes="Upper body focus"),
            Workout(date=today - timedelta(days=1), duration_minutes=30, notes="Cardio and core"),
            Workout(date=today, duration_minutes=60, notes="Full body"),
        ]
        db.session.add_all(workouts)
        db.session.commit()

        # Add random exercises to each workout
        for workout in workouts:
            # Pick 2-4 random exercises
            chosen = random.sample(exercises, random.randint(2, 4))
            for exercise in chosen:
                we = WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=exercise.id,
                    reps=random.choice([None, random.randint(8, 15)]),
                    sets=random.choice([None, random.randint(2, 4)]),
                    duration_seconds=random.choice([None, random.randint(30, 120)])
                )
                db.session.add(we)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed()