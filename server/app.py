from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutDetailSchema, ExerciseDetailSchema, WorkoutExerciseSchema
from marshmallow import ValidationError
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Error handlers
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify(e.messages), 400

@app.errorhandler(ValueError)
def handle_value_error(e):
    return jsonify({'error': str(e)}), 400

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

# ----- Workout endpoints -----
@app.route('/workouts', methods=['GET'])
def list_workouts():
    workouts = Workout.query.all()
    schema = WorkoutSchema(many=True)
    return jsonify(schema.dump(workouts))

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = Workout.query.get_or_404(id)
    schema = WorkoutDetailSchema()
    return jsonify(schema.dump(workout))

@app.route('/workouts', methods=['POST'])
def create_workout():
    data = request.get_json()
    schema = WorkoutSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    workout = Workout(**validated_data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(schema.dump(workout)), 201

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = Workout.query.get_or_404(id)
    # Cascade delete is configured on the relationship, so associated WorkoutExercises will be deleted
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout deleted'}), 200

# ----- Exercise endpoints -----
@app.route('/exercises', methods=['GET'])
def list_exercises():
    exercises = Exercise.query.all()
    schema = ExerciseSchema(many=True)
    return jsonify(schema.dump(exercises))

@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = Exercise.query.get_or_404(id)
    schema = ExerciseDetailSchema()
    return jsonify(schema.dump(exercise))

@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json()
    schema = ExerciseSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    exercise = Exercise(**validated_data)
    db.session.add(exercise)
    db.session.commit()
    return jsonify(schema.dump(exercise)), 201

@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = Exercise.query.get_or_404(id)
    # Cascade delete will remove WorkoutExercises
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({'message': 'Exercise deleted'}), 200

# ----- Add exercise to workout (WorkoutExercise creation) -----
@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get_or_404(workout_id)
    exercise = Exercise.query.get_or_404(exercise_id)
    data = request.get_json() or {}
    # Validate with WorkoutExerciseSchema (partial to allow missing fields)
    schema = WorkoutExerciseSchema(partial=('workout_id', 'exercise_id'))
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Create the join record
    we = WorkoutExercise(
        workout_id=workout.id,
        exercise_id=exercise.id,
        reps=validated_data.get('reps'),
        sets=validated_data.get('sets'),
        duration_seconds=validated_data.get('duration_seconds')
    )
    db.session.add(we)
    db.session.commit()
    return jsonify(schema.dump(we)), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)