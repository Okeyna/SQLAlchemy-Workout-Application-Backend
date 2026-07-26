from marshmallow import Schema, fields, validate, post_load, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import Exercise, Workout, WorkoutExercise, db

class WorkoutExerciseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = WorkoutExercise
        include_fk = True
        load_instance = True
        sqla_session = db.session

    # Schema validations: non-negative values
    reps = fields.Integer(validate=validate.Range(min=0), allow_none=True)
    sets = fields.Integer(validate=validate.Range(min=0), allow_none=True)
    duration_seconds = fields.Integer(validate=validate.Range(min=0), allow_none=True)

class ExerciseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Exercise
        load_instance = True
        sqla_session = db.session

    # Schema validation: name length >=1
    name = fields.String(validate=validate.Length(min=1), required=True)

class WorkoutSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Workout
        load_instance = True
        sqla_session = db.session

    # Schema validation: duration positive
    duration_minutes = fields.Integer(validate=validate.Range(min=1), required=True)
    date = fields.Date(required=True)

# Nested schemas for detailed responses
class WorkoutExerciseDetailSchema(WorkoutExerciseSchema):
    exercise = fields.Nested(ExerciseSchema, only=('id', 'name', 'category', 'equipment_needed'))

class WorkoutDetailSchema(WorkoutSchema):
    workout_exercises = fields.Nested(WorkoutExerciseDetailSchema, many=True)

class ExerciseDetailSchema(ExerciseSchema):
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True)