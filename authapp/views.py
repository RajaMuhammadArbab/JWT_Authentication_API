import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from django.conf import settings
from .serializers import LoginSerializer, RefreshSerializer, LogoutSerializer
from .utils import create_access_token, create_refresh_token, decode_token, verify_refresh_token_in_db, revoke_refresh_token
from .models import RefreshToken
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
def register(request):
    """
    Register a new user
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    return Response({"message": f"User {user.username} created successfully"}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        access, _ = create_access_token(user)
        refresh_raw, refresh_obj = create_refresh_token(user)

        return Response({
            'access': access,
            'refresh': refresh_raw,
            'access_expires_in': settings.JWT['ACCESS_TOKEN_LIFETIME_SECONDS'],
            'refresh_expires_in': settings.JWT['REFRESH_TOKEN_LIFETIME_SECONDS'],
        })

class RefreshAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_refresh = serializer.validated_data['refresh']

        
        try:
            payload = decode_token(raw_refresh, verify_exp=True)
        except Exception as e:
            return Response({'detail': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        if payload.get('type') != 'refresh' or 'jti' not in payload:
            return Response({'detail': 'Invalid token type'}, status=status.HTTP_401_UNAUTHORIZED)

        jti = payload['jti']
        
        rt = verify_refresh_token_in_db(raw_refresh, jti)
        if rt is None:
            
            return Response({'detail': 'Refresh token invalid or revoked'}, status=status.HTTP_401_UNAUTHORIZED)

        
        revoke_refresh_token(rt)
        new_raw_refresh, new_rt = create_refresh_token(rt.user, rotated_from_jti=rt.jti)
        
        new_access, _ = create_access_token(rt.user)

        return Response({
            'access': new_access,
            'refresh': new_raw_refresh,
            'access_expires_in': settings.JWT['ACCESS_TOKEN_LIFETIME_SECONDS'],
            'refresh_expires_in': settings.JWT['REFRESH_TOKEN_LIFETIME_SECONDS'],
        })

class LogoutAPIView(APIView):
    permission_classes = [permissions.AllowAny]
   

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_refresh = serializer.validated_data.get('refresh', None)
        all_sessions = request.data.get('all', False)

        if all_sessions:
            
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]
                try:
                    payload = decode_token(access_token, verify_exp=False)
                except Exception:
                    return Response({'detail': 'Invalid access token'}, status=status.HTTP_401_UNAUTHORIZED)
                user_id = payload.get('user_id')
                if not user_id:
                    return Response({'detail': 'Invalid token payload'}, status=status.HTTP_400_BAD_REQUEST)
                
                RefreshToken.objects.filter(user_id=user_id, revoked=False).update(revoked=True)
                django_logout(request)
                return Response({'detail': 'All sessions logged out'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Provide access token in Authorization header to logout all sessions'}, status=status.HTTP_400_BAD_REQUEST)

        if not raw_refresh:
            return Response({'detail': 'Provide a refresh token or set all=true'}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            payload = decode_token(raw_refresh, verify_exp=False)
        except Exception:
            return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        jti = payload.get('jti')
        try:
            rt = RefreshToken.objects.get(jti=jti)
            rt.revoked = True
            rt.save(update_fields=['revoked'])
            return Response({'detail': 'Logged out (refresh token revoked)'}, status=status.HTTP_200_OK)
        except RefreshToken.DoesNotExist:
            return Response({'detail': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from django.contrib.auth import get_user_model

User = get_user_model()

def get_user_from_access_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        raise exceptions.NotAuthenticated('Authorization header missing or not Bearer')
    token = auth_header.split(' ')[1]
    try:
        payload = decode_token(token, verify_exp=True)
    except jwt.ExpiredSignatureError:
        raise exceptions.NotAuthenticated('Access token expired')
    except Exception:
        raise exceptions.NotAuthenticated('Invalid access token')
    if payload.get('type') != 'access':
        raise exceptions.AuthenticationFailed('Token is not access type')

    user_id = payload.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed('User not found')
    return user

class ProtectedAPIView(APIView):
    permission_classes = [permissions.AllowAny] 
    def get(self, request):
        try:
            user = get_user_from_access_token(request)
        except exceptions.APIException as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'detail': f'Hello, {user.username}. This is a protected view.'})
