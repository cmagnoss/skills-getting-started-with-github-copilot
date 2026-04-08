import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

# Copiar o estado inicial das atividades para reset
initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))

@pytest.fixture
def client():
    return TestClient(app)

def test_get_activities(client):
    # Arrange
    # (nenhuma preparação necessária, atividades já resetadas)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Deve ter 9 atividades
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"

def test_signup_success(client):
    # Arrange
    activity_name = "Basketball Team"  # Começa vazio
    email = "test@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    # Verificar que foi adicionado
    assert email in activities[activity_name]["participants"]

def test_signup_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up(client):
    # Arrange
    activity_name = "Chess Club"  # Já tem participantes
    email = "michael@mergington.edu"  # Já inscrito

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]

def test_signup_activity_full(client):
    # Arrange
    activity_name = "Chess Club"  # max 12, já tem 2
    # Adicionar participantes até encher
    for i in range(10):
        email = f"student{i}@mergington.edu"
        activities[activity_name]["participants"].append(email)
    # Agora tem 12, cheio
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Activity is full" in data["detail"]

def test_unregister_success(client):
    # Arrange
    activity_name = "Programming Class"  # Tem 2 participantes
    email = "emma@mergington.edu"  # Está inscrito

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    # Verificar que foi removido
    assert email not in activities[activity_name]["participants"]

def test_unregister_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_not_signed_up(client):
    # Arrange
    activity_name = "Art Club"  # Vazio
    email = "notsigned@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up for this activity" in data["detail"]