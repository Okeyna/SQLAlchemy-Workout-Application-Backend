from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutDetailSchema, ExerciseDetailSchema, WorkoutExerciseSchema
from marshmallow import ValidationError

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
    workout = db.session.get(Workout, id)
    if workout is None:
        abort(404)
    schema = WorkoutDetailSchema()
    return jsonify(schema.dump(workout))

@app.route('/workouts', methods=['POST'])
def create_workout():
    data = request.get_json()
    schema = WorkoutSchema()
    try:
        workout = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    db.session.add(workout)
    db.session.commit()
    return jsonify(schema.dump(workout)), 201

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        abort(404)
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
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        abort(404)
    schema = ExerciseDetailSchema()
    return jsonify(schema.dump(exercise))

@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json()
    schema = ExerciseSchema()
    try:
        exercise = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    db.session.add(exercise)
    db.session.commit()
    return jsonify(schema.dump(exercise)), 201

@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        abort(404)
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({'message': 'Exercise deleted'}), 200

# ----- Add exercise to workout -----
@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        abort(404)
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        abort(404)
    data = request.get_json() or {}
    schema = WorkoutExerciseSchema(partial=('workout_id', 'exercise_id'))
    try:
        we = schema.load(data)
        we.workout_id = workout.id
        we.exercise_id = exercise.id
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(we)
    db.session.commit()
    return jsonify(WorkoutExerciseSchema().dump(we)), 201

if __name__ == '__main__':
    app.run(debug=True)