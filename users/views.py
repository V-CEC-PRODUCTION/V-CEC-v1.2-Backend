from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from .models import User
from .serializers import UserSerializer

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