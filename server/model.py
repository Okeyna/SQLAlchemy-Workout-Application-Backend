from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from datetime import date

db = SQLAlchemy()

class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    equipment_needed = db.Column(db.Boolean, default=False)

    # Table constraint: name must be unique
    __table_args__ = (
        UniqueConstraint('name', name='uq_exercise_name'),
    )

    # Model validations
    @db.validates('name')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name cannot be empty.")
        return value.strip()

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan')
    workouts = db.relationship('Workout', secondary='workout_exercises', back_populates='exercises')

    def __repr__(self):
        return f'<Exercise {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Table constraint: duration must be positive
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    # Model validations
    @db.validates('date')
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("Workout date cannot be null.")
        return value

    @db.validates('duration_minutes')
    def validate_duration(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Duration must be a positive integer.")
        return value

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', back_populates='workout', cascade='all, delete-orphan')
    exercises = db.relationship('Exercise', secondary='workout_exercises', back_populates='workouts')

    def __repr__(self):
        return f'<Workout {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id', ondelete='CASCADE'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id', ondelete='CASCADE'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Table constraints: reps, sets, duration must be >= 0 if provided
    __table_args__ = (
        CheckConstraint('reps >= 0', name='ck_workout_exercise_reps_nonneg'),
        CheckConstraint('sets >= 0', name='ck_workout_exercise_sets_nonneg'),
        CheckConstraint('duration_seconds >= 0', name='ck_workout_exercise_duration_nonneg'),
    )

    # Relationships
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # Model validations
    @db.validates('reps')
    def validate_reps(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Reps must be non-negative.")
        return value

    @db.validates('sets')
    def validate_sets(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Sets must be non-negative.")
        return value

    @db.validates('duration_seconds')
    def validate_duration(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Duration seconds must be non-negative.")
        return value

    def __repr__(self):
        return f'<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>'from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from datetime import date

db = SQLAlchemy()

class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    equipment_needed = db.Column(db.Boolean, default=False)

    # Table constraint: name must be unique
    __table_args__ = (
        UniqueConstraint('name', name='uq_exercise_name'),
    )

    # Model validations
    @db.validates('name')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name cannot be empty.")
        return value.strip()

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan')
    workouts = db.relationship('Workout', secondary='workout_exercises', back_populates='exercises')

    def __repr__(self):
        return f'<Exercise {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Table constraint: duration must be positive
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    # Model validations
    @db.validates('date')
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("Workout date cannot be null.")
        return value

    @db.validates('duration_minutes')
    def validate_duration(self, key, value):
        if value is None or value <= 0:
            raise ValueError("Duration must be a positive integer.")
        return value

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', back_populates='workout', cascade='all, delete-orphan')
    exercises = db.relationship('Exercise', secondary='workout_exercises', back_populates='workouts')

    def __repr__(self):
        return f'<Workout {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id', ondelete='CASCADE'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id', ondelete='CASCADE'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Table constraints: reps, sets, duration must be >= 0 if provided
    __table_args__ = (
        CheckConstraint('reps >= 0', name='ck_workout_exercise_reps_nonneg'),
        CheckConstraint('sets >= 0', name='ck_workout_exercise_sets_nonneg'),
        CheckConstraint('duration_seconds >= 0', name='ck_workout_exercise_duration_nonneg'),
    )

    # Relationships
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # Model validations
    @db.validates('reps')
    def validate_reps(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Reps must be non-negative.")
        return value

    @db.validates('sets')
    def validate_sets(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Sets must be non-negative.")
        return value

    @db.validates('duration_seconds')
    def validate_duration(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Duration seconds must be non-negative.")
        return value

    def __repr__(self):
        return f'<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>'