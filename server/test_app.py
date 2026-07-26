import pytest
from app import app
from models import db, Exercise, Workout, WorkoutExercise
from datetime import date

@pytest.fixture
def client():
    """Set up a test client with an in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.drop_all()          # <-- add this line to clear any existing data
        db.create_all()
        # Seed some test data
        exercise1 = Exercise(name="Push-up", category="Strength", equipment_needed=False)
        exercise2 = Exercise(name="Squat", category="Strength", equipment_needed=False)
        workout1 = Workout(date=date(2026, 7, 25), duration_minutes=30, notes="Test workout")
        db.session.add_all([exercise1, exercise2, workout1])
        db.session.commit()
        we = WorkoutExercise(
            workout_id=workout1.id,
            exercise_id=exercise1.id,
            reps=10,
            sets=3,
            duration_seconds=None
        )
        db.session.add(we)
        db.session.commit()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.drop_all()


def test_get_workouts(client):
    """GET /workouts returns a list of workouts."""
    response = client.get('/workouts')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['date'] == '2026-07-25'
    assert data[0]['duration_minutes'] == 30


def test_get_workout_detail(client):
    """GET /workouts/<id> returns workout with nested exercises."""
    response = client.get('/workouts/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 1
    assert data['date'] == '2026-07-25'
    assert data['notes'] == 'Test workout'
    # Check nested workout_exercises
    assert len(data['workout_exercises']) == 1
    we = data['workout_exercises'][0]
    assert we['reps'] == 10
    assert we['sets'] == 3
    assert we['exercise']['name'] == 'Push-up'


def test_create_workout(client):
    """POST /workouts creates a new workout."""
    payload = {
        'date': '2026-07-26',
        'duration_minutes': 45,
        'notes': 'New workout'
    }
    response = client.post('/workouts', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['date'] == '2026-07-26'
    assert data['duration_minutes'] == 45
    # Verify it was added
    get_resp = client.get('/workouts')
    assert len(get_resp.get_json()) == 2


def test_create_workout_validation_error(client):
    """POST /workouts with invalid duration triggers validation."""
    payload = {
        'date': '2026-07-26',
        'duration_minutes': -5,  # invalid
        'notes': 'Invalid'
    }
    response = client.post('/workouts', json=payload)
    assert response.status_code == 400
    assert 'duration_minutes' in response.get_json()


def test_delete_workout(client):
    """DELETE /workouts/<id> deletes workout and cascade removes WorkoutExercises."""
    # First verify there is a workout exercise
    resp = client.get('/workouts/1')
    assert resp.status_code == 200
    assert len(resp.get_json()['workout_exercises']) == 1

    # Delete
    response = client.delete('/workouts/1')
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Workout deleted'}

    # Check it's gone
    get_resp = client.get('/workouts/1')
    assert get_resp.status_code == 404

    # Check the associated WorkoutExercise is also deleted (would be cascade)
    # We can't directly check via endpoint, but we can query the db
    with app.app_context():
        count = WorkoutExercise.query.filter_by(workout_id=1).count()
        assert count == 0


def test_get_exercises(client):
    """GET /exercises returns all exercises."""
    response = client.get('/exercises')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 2
    names = [e['name'] for e in data]
    assert 'Push-up' in names
    assert 'Squat' in names


def test_get_exercise_detail(client):
    """GET /exercises/<id> returns exercise with associated workouts."""
    response = client.get('/exercises/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Push-up'
    assert len(data['workout_exercises']) == 1
    assert data['workout_exercises'][0]['workout_id'] == 1


def test_create_exercise(client):
    """POST /exercises creates a new exercise."""
    payload = {
        'name': 'Deadlift',
        'category': 'Strength',
        'equipment_needed': True
    }
    response = client.post('/exercises', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Deadlift'
    assert data['equipment_needed'] is True
    # Verify it exists
    get_resp = client.get('/exercises')
    names = [e['name'] for e in get_resp.get_json()]
    assert 'Deadlift' in names


def test_create_exercise_validation_error(client):
    """POST /exercises with empty name triggers validation."""
    payload = {
        'name': '',  # invalid
        'category': 'Cardio',
        'equipment_needed': False
    }
    response = client.post('/exercises', json=payload)
    assert response.status_code == 400
    # Marshmallow error for length
    assert 'name' in response.get_json()


def test_delete_exercise(client):
    """DELETE /exercises/<id> deletes exercise and cascade removes WorkoutExercises."""
    # Create a new exercise and add it to workout 1 to test cascade
    with app.app_context():
        new_ex = Exercise(name="Lunges", category="Strength", equipment_needed=False)
        db.session.add(new_ex)
        db.session.commit()
        # Link it to workout 1
        we = WorkoutExercise(workout_id=1, exercise_id=new_ex.id, reps=12, sets=4)
        db.session.add(we)
        db.session.commit()
        ex_id = new_ex.id

    # Delete the exercise
    response = client.delete(f'/exercises/{ex_id}')
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Exercise deleted'}

    # Check exercise is gone
    get_resp = client.get(f'/exercises/{ex_id}')
    assert get_resp.status_code == 404

    # Check WorkoutExercise is gone (cascade)
    with app.app_context():
        count = WorkoutExercise.query.filter_by(exercise_id=ex_id).count()
        assert count == 0


def test_add_exercise_to_workout(client):
    """POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises adds an exercise to a workout."""
    # Use exercise 2 (Squat) which is not yet in workout 1
    payload = {
        'reps': 15,
        'sets': 4,
        'duration_seconds': 60
    }
    response = client.post('/workouts/1/exercises/2/workout_exercises', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['reps'] == 15
    assert data['sets'] == 4
    assert data['duration_seconds'] == 60
    assert data['workout_id'] == 1
    assert data['exercise_id'] == 2

    # Verify the workout now has two exercises
    detail = client.get('/workouts/1').get_json()
    assert len(detail['workout_exercises']) == 2


def test_add_exercise_to_workout_partial_data(client):
    """POST with optional fields omitted is fine."""
    payload = {
        'reps': 20
    }
    response = client.post('/workouts/1/exercises/2/workout_exercises', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['reps'] == 20
    assert data['sets'] is None
    assert data['duration_seconds'] is None


def test_add_exercise_to_workout_negative_value(client):
    """POST with negative reps triggers validation."""
    payload = {
        'reps': -5,
        'sets': 3
    }
    response = client.post('/workouts/1/exercises/2/workout_exercises', json=payload)
    assert response.status_code == 400
    assert 'reps' in response.get_json()


def test_get_nonexistent_workout(client):
    """GET /workouts/<invalid_id> returns 404."""
    response = client.get('/workouts/999')
    assert response.status_code == 404


def test_get_nonexistent_exercise(client):
    """GET /exercises/<invalid_id> returns 404."""
    response = client.get('/exercises/999')
    assert response.status_code == 404


def test_delete_nonexistent_workout(client):
    """DELETE /workouts/<invalid_id> returns 404."""
    response = client.delete('/workouts/999')
    assert response.status_code == 404