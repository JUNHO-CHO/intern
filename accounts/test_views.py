import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser




@pytest.mark.django_db
def test_signup(client):
    url = reverse('signup')  # URL 이름에 맞게 수정하세요
    data = {
        'username': 'testuser',
        'nickname': 'testnick',
        'password': 'testpassword'
    }

    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(username='testuser').exists()

@pytest.mark.django_db
def test_signup_username_already_exists(client):
    CustomUser.objects.create_user(username='testuser', password='testpassword', nickname='testnick')
    url = reverse('signup')
    data = {
        'username': 'testuser',
        'nickname': 'newnick',
        'password': 'testpassword'
    }

    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data['error']

@pytest.mark.django_db
def test_login(client):
    user = CustomUser.objects.create_user(
        username='testuser',
        password='testpassword',
        nickname='testnick'
    )

    url = reverse('login')
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }

    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

@pytest.mark.django_db
def test_login_invalid_credentials(client):
    url = reverse('login')
    data = {
        'username': 'testuser',
        'password': 'wrongpassword'
    }

    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'INVALID_CREDENTIALS' in response.data['error']['code']

@pytest.mark.django_db
def test_validate_token(client):
    user = CustomUser.objects.create_user(
        username='testuser',
        password='testpassword',
        nickname='testnick'
    )
    refresh = RefreshToken.for_user(user)
    
    url = reverse('validate_token')
    headers = {
        'Authorization': f'Bearer {refresh.access_token}'
    }

    response = client.get(url, **headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '토큰이 유효합니다.'

@pytest.mark.django_db
def test_validate_token(client):
    user = CustomUser.objects.create_user(
        username='testuser',
        password='testpassword',
        nickname='testnick'
    )
    refresh = RefreshToken.for_user(user)

    url = reverse('validate_token')
    headers = {
        'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'  # HTTP_ 접두사 추가
    }

    response = client.get(url, **headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == '토큰이 유효합니다.'