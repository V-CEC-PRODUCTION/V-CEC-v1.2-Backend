from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist   
from django.core.mail import send_mail
from .models import User
from .serializers import UserSerializer, EmailSerializer, OtpSerializer
import random
from datetime import datetime, timedelta

@api_view(['POST'])
def send_otp(request):
    serializer = EmailSerializer(data=request.data)
    if serializer.is_valid():
        user_email = serializer.validated_data['user_email']
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        subject = 'Your OTP'
        message = f'Your OTP is: {otp}'
        from_email = 'proddecapp@gmail.com'

        send_mail(subject, message, from_email, [user_email])

        # Convert the datetime to a string
        expiry_time = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')

        request.session['otp'] = {
            'code': otp,
            'expiry': expiry_time
        }

        return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
    
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify(request):
    serializer = OtpSerializer(data=request.data)
    if serializer.is_valid():
        user_entered_otp = serializer.validated_data['user_otp']
        stored_otp_data = request.session.get('otp')

        if stored_otp_data and str(datetime.now()) < stored_otp_data['expiry']:
            stored_otp = stored_otp_data['code']
            if user_entered_otp == stored_otp:
                request.session.pop('otp', None)
                return Response({'message': 'OTP verification successful.'}, status=status.HTTP_200_OK)
        return Response({'error': 'OTP verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
# get all users
@api_view(['GET'])
def get_all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response({'all_users': serializer.data})

#get user by id
@api_view(['GET'])
def get_user_by_id(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

# create user
@api_view(['POST'])
def create_user(request):
    try:
        data = request.data.copy()
        
        if 'password' in data:
            data['password'] = make_password(data['password'])
        
        serializer = UserSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except KeyError as e:
        return Response(f"Missing key: {str(e)}", status=status.HTTP_400_BAD_REQUEST)
    
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"detail": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# update user
@api_view(['PUT'])
def update_user(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(instance=user, data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        
    return Response(serializer.data)


# delete user
@api_view(['DELETE'])
def delete_user(request, pk):
     
    try:
        user = User.objects.get(id=pk)
        
        user.delete()
    
        return Response("User deleted successfully!", status=status.HTTP_204_NO_CONTENT)
    
    except ObjectDoesNotExist:
        return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
    
    
# login user
@api_view(['POST'])
def login_user(request):
    try:
        user = User.objects.get(email=request.data['email'])
        
        if check_password(request.data['password'], user.password):
            user.logged_in = True
            user.save()
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        else:
            return Response("Password is incorrect!", status=status.HTTP_400_BAD_REQUEST)
    
    except ObjectDoesNotExist:
        return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)
    
# logout user
@api_view(['POST'])
def logout_user(request):
    try:
        user = User.objects.get(email=request.data['email'])
        
        if user.logged_in:
            user.logged_in = False
            user.save()
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        else:
            return Response("User is not logged in!", status=status.HTTP_400_BAD_REQUEST)
    
    except ObjectDoesNotExist:
        return Response("User does not exist!", status=status.HTTP_404_NOT_FOUND)