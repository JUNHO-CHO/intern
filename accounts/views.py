import jwt
import datetime
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from .models import CustomUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)

    errors = {}
    username = request.data.get('username')
    nickname = request.data.get('nickname')

    # 사용자 이름 중복 체크
    if username and CustomUser.objects.filter(username=username).exists():
        errors['username'] = {
            "code": "USERNAME_ALREADY_EXISTS",
            "message": "이미 가입된 사용자 이름입니다."
        }

    # 닉네임 중복 체크
    if nickname and CustomUser.objects.filter(nickname=nickname).exists():
        errors['nickname'] = {
            "code": "NICKNAME_ALREADY_EXISTS",
            "message": "이미 가입된 닉네임입니다."
        }

    # 중복된 필드가 있을 경우 오류 반환
    if errors:
        return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)

    # serializer 유효성 검사
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 기본 유효성 검사 오류 처리
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            'error': {
                'code': 'INVALID_CREDENTIALS',
                'message': '아이디와 비밀번호가 맞지 않습니다.'
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user) 
        access_token = str(refresh.access_token)  

        return Response({
            'access': access_token,
            'refresh': str(refresh) 
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': {
            'code': 'INVALID_CREDENTIALS',
            'message': '아이디 또는 비밀번호가 올바르지 않습니다.'
        }
    }, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='get',
    operation_summary="토큰 유효성 검사",
    responses={
        200: openapi.Response('토큰이 유효합니다.', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, example='토큰이 유효합니다.')
        })),
        401: openapi.Response('유효하지 않은 토큰', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'error': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            })
        }))
    }
)
@api_view(['GET'])
def validate_token(request):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            'error': {
                'code': 'TOKEN_NOT_FOUND',
                'message': '토큰이 없습니다.'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)

    try:
        access_token = token.split()[1]
        
        # JWT 서명 검증을 활성화
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = decoded.get('exp')

        if exp and exp < datetime.datetime.utcnow().timestamp():
            return Response({
                'error': {
                    'code': 'TOKEN_EXPIRED',
                    'message': '토큰이 만료되었습니다.'
                }
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'message': '토큰이 유효합니다.'
        }, status=status.HTTP_200_OK)

    except InvalidToken:
        return Response({
            'error': {
                'code': 'INVALID_TOKEN',
                'message': '토큰이 유효하지 않습니다.'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({
            'error': {
                'code': 'UNKNOWN_ERROR',
                'message': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
