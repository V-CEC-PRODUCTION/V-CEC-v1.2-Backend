from django.shortcuts import render
from rest_framework.decorators import api_view
import pandas as pd
from .serializers import TimeTableCurrentSerializer, TimeTableSerializer,TimeTableAdminSerializer,TimeTableClientSerializer             
from rest_framework.response import Response
from rest_framework import status
from .models import TimeTable
from rest_framework.views import APIView
from users.models import User, Token
from users.utils import TokenUtil
from datetime import datetime, time

from django.http import HttpRequest

def get_base_url(request: HttpRequest):
    base_url = request.build_absolute_uri('/')[:-1]  # Get base URL without trailing slash
    return base_url

# Create your views here.
@api_view(['POST'])
def create_timetables(request):
    if request.data.get("excel_sheet"):
        file_path = request.data.get("excel_sheet")
        df = pd.read_excel(file_path)
        tt=df.to_dict(orient='dict')
    
        fields=['firstcode','secondcode','thirdcode','fourthcode','fifthcode','sixthcode','day','semester','division']
        listofrcrd=list(tt['day'].keys())
        
    
        for i in listofrcrd:
            data={}
            for  j in fields:
                data[j]=tt[j][i]
            if data['day']==5:
                data['firsttime']='09:00 AM-09:50 AM'
                data['secondtime']='09:50 AM-10:40 AM'
                data['thirdtime']='10:50 AM-11:40 AM'
                data['fourthtime']='11:40 AM-12:30 PM'
            serializer=TimeTableSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def create_timetable(request):
    serializer=TimeTableSerializer(data=request.data)
    if serializer.is_valid():
        serializer_instance=serializer.save()

        if serializer.data['day']==5:
            serializer_instance.firsttime='09:00 AM-09:50 AM'
            serializer_instance.secondtime='09:50 AM-10:40 AM'
            serializer_instance.thirdtime='10:50 AM-11:40 AM'
            serializer_instance.fourthtime='11:40 AM-12:30 PM'
            
        serializer_instance.save()
        
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_timetables(request):
    try:
        timetable = TimeTable.objects.all()

        serializer = TimeTableAdminSerializer(timetable, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TimeTable.DoesNotExist:
        return Response({"status": "Timetables not found"}, status=status.HTTP_404_NOT_FOUND)

#get for client    
@api_view(['GET'])
def get_clienttimetables(request):
    try:
 
        authorization_header = request.META.get("HTTP_AUTHORIZATION")
            
        if not authorization_header:
            return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)


        _, token = authorization_header.split()
        
        token_key = Token.objects.filter(access_token=token).first()
        
        if not token_key:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)
        

        payload = TokenUtil.decode_token(token_key.access_token)

        # Optionally, you can extract user information or other claims from the payload
        if not payload:
            return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the refresh token is associated with a user (add your logic here)
        user_id = payload.get('id')
        
        if not user_id:
            return Response({'error': 'The access token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = User.objects.get(id=user_id) 
        
        dt = datetime.now()
        
        day = dt.weekday() - 1
        

        semester = str(user.semester)[1]
                    
        
        timetable = TimeTable.objects.filter(semester=semester,division=user.division,day=day)

        serializer = TimeTableClientSerializer(timetable, many=True)
        for data in serializer.data:
            for field in ['firsttime', 'secondtime', 'thirdtime', 'fourthtime', 'fifthtime', 'sixthtime']:
                data[field] = data[field].split("-")[0]
        
        return Response({"result":serializer.data}, status=status.HTTP_200_OK)
    except TimeTable.DoesNotExist:
        return Response({"status": "Timetables not found"}, status=status.HTTP_404_NOT_FOUND)


#cuurentcode, current time

class GetCurrentCode(APIView):
    def get(self,request):
        try:
            authorization_header = request.META.get("HTTP_AUTHORIZATION")
                
            if not authorization_header:
                return Response({"error": "Access token is missing."}, status=status.HTTP_401_UNAUTHORIZED)


            _, token = authorization_header.split()
            
            token_key = Token.objects.filter(access_token=token).first()
            
            if not token_key:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)
            

            payload = TokenUtil.decode_token(token_key.access_token)

            # Optionally, you can extract user information or other claims from the payload
            if not payload:
                return Response({"error": "Invalid access token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the refresh token is associated with a user (add your logic here)
            user_id = payload.get('id')
            
            if not user_id:
                return Response({'error': 'The access token is not associated with a user.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user = User.objects.get(id=user_id) 
                
            
            if user.role == 'student':
                dt = datetime.now()
                
                day = dt.weekday()
                
                currenttime = dt.time().hour
                
                print(currenttime)
                
                if day in [5,6]:
                    day = 1
                else:
                    day = day + 1 

                semester = str(user.semester)[1]    
                
                timetable = TimeTable.objects.filter(semester=semester,division=user.division,day=day)

                serializer = TimeTableClientSerializer(timetable, many=True)
                
                for data in serializer.data:
                    for field in ['firsttime', 'secondtime', 'thirdtime', 'fourthtime', 'fifthtime', 'sixthtime']:
                        data[field] = data[field].split("-")[0]
                        data[field] = data[field].split(" ")[0]
            
              

                if user.image_url != None or user.thumbnail_url != None:
                    return Response({"result": serializer.data,"thumbnail_url": user.thumbnail_url, "image_thumbnail_url": user.image_url, "name": user.name}, status=status.HTTP_200_OK)
            
            else:   
                return Response({"result": [
        {
            "firstcode": "",
            "secondcode": "",
            "thirdcode": "",
            "fourthcode": "",
            "fifthcode": "",
            "sixthcode": "",
            "firsttime": "",
            "secondtime": "",
            "thirdtime": "",
            "fourthtime": "",
            "fifthtime": "",
            "sixthtime": "",
            "currentcode": "",
            "currenttime": ""
        }
    ],"thumbnail_url": user.thumbnail_url, "image_thumbnail_url": user.image_url, "name": user.name}, status=status.HTTP_200_OK)
            
        except TimeTable.DoesNotExist:
            return Response({"status": "Timetables not found"}, status=status.HTTP_404_NOT_FOUND)
            

@api_view(['PUT'])
def update_timetable(request,semester,division,day):
    timetable_data = TimeTable.objects.get(semester=semester, division=division, day=day)
    if request.data.get('firstcode'):
        timetable_data.firstcode = request.data.get('firstcode')
    if request.data.get('secondcode'):
        timetable_data.secondcode = request.data.get('secondcode')
    if request.data.get('thirdcode'):
        timetable_data.thirdcode = request.data.get('thirdcode')
    if request.data.get('fourthcode'):
        timetable_data.fourthcode = request.data.get('fourthcode')
    if request.data.get('fifthcode'):
        timetable_data.fifthcode = request.data.get('fifthcode')
    if request.data.get('sixthcode'):
        timetable_data.sixthcode = request.data.get('sixthcode')
    timetable_data.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_timetable(request, semester, division=None, day=None):
    try:
        #Specific day timetable deletion
        if day is not None:
            timetable = TimeTable.objects.get(semester=semester, division=division.upper(), day=day)
            timetable.delete()
            return Response({"status": f"Timetable for S{semester}{division}'s day {day} deleted successfully"}, status=status.HTTP_200_OK)
        elif division is not None:
            # Delete a specific divison's timetable
            timetables = TimeTable.objects.filter(semester=semester, division=division.upper())
            timetables.delete()
            return Response({"status": f"Timetable for S{semester}{division} deleted successfully"}, status=status.HTTP_200_OK)
        else:
            # Delete the entire semester's timetable 
            timetables = TimeTable.objects.filter(semester=semester)
            timetables.delete()
            return Response({"status": f"Timetable for Semester :{semester} deleted successfully"}, status=status.HTTP_200_OK)
    except TimeTable.DoesNotExist:
        return Response({"status": "Timetable records not found"}, status=status.HTTP_404_NOT_FOUND)
    

    




        