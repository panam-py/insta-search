from fastapi.testclient import TestClient

import pytest

from .main import app

client = TestClient(app)

def test_register():
    """
    Testing the "/register" endpoint of the application
    """
    endpoint = "/register"

    # Constructing data with wrong email format and sending request
    data = {"email": "testuser1", "password": "testpassword"}
    response = client.post(endpoint, json = data)

    # Making sure that the response is a bad one - 422 (unprocessable entity)
    assert response.status_code == 422

    # Correcting the email and retrying request
    data["email"] = "test@gmail.com"
    response = client.post(endpoint, json = data)

    # Making sure the response is a good one
    assert response.status_code == 201
    # Making sure the status of the response is "success"
    assert response.json()["status"] == "success"
    # Making sure the email is the same as was sent
    assert response.json()["data"]["email"] == data["email"]
    # Making sure password was stripped from the returned user
    assert "password" not in response.json().keys()

    # Retrying another registration request with an email that has 
    # already been used an making sure that the response is a bad one
    response = client.post(endpoint, json = data)
    assert response.status_code == 403


def test_login_and_refresh():
    """
    Testing the "/login" endpoint of the application
    """
    endpoint = "/login"

    # Constructing data to send to request with a wrong password
    # and sending request
    data = {"email": "test@gmail.com", "password": "testpasswor"}
    response = client.post(endpoint, json = data)

    # Making sure the response is a bad one
    assert response.status_code == 401

    # Sending another request with a wrong email address, sending 
    # another request and making sure response is bad
    data["email"] = "notatestuser@gmail.com"
    response = client.post(endpoint, json = data)
    assert response.status_code == 401

    # Correcting details and sending request, also making sure
    # the details are correct
    data["email"] = "test@gmail.com"
    data["password"] = "testpassword"
    response = client.post(endpoint, json = data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["email"] == data["email"]
    assert "password" not in response.json()["data"].keys()
    assert "access_token" in response.json().keys()
    assert "refresh_token" in response.json().keys()


def test_refresh():
    """
    Testing the "/refresh endpoint
    """
    endpoint = "/refresh"

    # Sending request
    response = client.get(endpoint)

    # Making sure the response is good
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "access_token" in response.json().keys()


def test_onboarding():
    """
    Testing the "/onboarding" endpoint 
    """
    endpoint = "/onboarding"

    # Constructing data, sending request and asserting response
    data = {"username": "test", "follower_count": 100, "bio": "Instagram influencer"}
    # Setting "bio" field to be more than 100 characters
    data["bio"] *= 200
    response = client.post(endpoint, json = data)
    assert response.status_code == 422
    
    # Correcting data, retrying request and asserting response
    data["bio"] = "Instagram influencer"
    response = client.post(endpoint, json = data)
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["data"]["username"] == data["username"]

    # Retrying request with the same username
    response = client.post(endpoint, json = data)
    assert response.status_code == 403

    # Trying to create an influencer with different username for user
    data["username"] = "testuser1"
    response = client.post(endpoint, json = data)
    assert response.status_code == 403


def test_search():
    """
    Testing the "/search" endpoint
    """
    min_followers = 99
    max_followers = 200
    keyword = "instagram"

    endpoint = "/search?min_followers=" + str(min_followers) + "&max_followers=" + str(max_followers) + "&keyword=" + keyword

    # Sending request
    response = client.get(endpoint)    

    # Asserting response
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["count"] == len(response.json()["data"])
    assert response.json()["count"] > 0
    for data in response.json()["data"]:
        assert data["follower_count"] <= max_followers
        assert data["follower_count"] >= min_followers


def test_logout():
    """
    Tests the "/logout" endpoint of the app
    """

    endpoint = "/logout"

    # Send request and assert that cookies were cleared
    response = client.get(endpoint)
    print(response.cookies)
    assert len(response.cookies.keys()) < 1
