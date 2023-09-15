from django.shortcuts import render
from rest_framework.decorators import api_view
import pandas as pd
from .serializers import TimeTableCurrentSerializer, TimeTableSerializer,TimeTableAdminSerializer,TimeTableClientSerializer             
from rest_framework.response import Response
from rest_framework import status
from .models import TimeTable
from datetime import datetime,time
# Create your views here.
@api_view(['POST'])
def create_timetables(request):
    if request.data.get("excel_sheet"):
        file_path = request.data.get("excel_sheet")
        df = pd.read_excel(file_path)
        tt=df.to_dict(orient='dict')
    
        fields=['firstcode','secondcode','thirdcode','fourthcode','fifthcode','sixthcode','day','semester','division']
        listofrcrd=list(tt['day'].keys())
        data={}
    
        for i in listofrcrd:
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
        timetable = TimeTable.objects.all()
        
        serializer = TimeTableClientSerializer(timetable, many=True)
        for data in serializer.data:
            for field in ['firsttime', 'secondtime', 'thirdtime', 'fourthtime', 'fifthtime', 'sixthtime']:
                data[field] = data[field].split("-")[0]
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TimeTable.DoesNotExist:
        return Response({"status": "Timetables not found"}, status=status.HTTP_404_NOT_FOUND)


#cuurentcode, current time
@api_view(['GET'])
def get_currentcodetime(request,id):
    try:
        timetable = TimeTable.objects.filter(pk=id)

        serializer = TimeTableCurrentSerializer(timetable, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TimeTable.DoesNotExist:
        return Response({"status": "Timetables not found"}, status=status.HTTP_404_NOT_FOUND)
            



@api_view(['DELETE'])
def delete_timetable(request, semester, division=None, day=None):
    try:
        #Specific day timetable deletion
        if day is not None:
            timetable = TimeTable.objects.get(semester=semester, division=division, day=day)
            timetable.delete()
            return Response({"status": f"Timetable for S{semester}{division}'s day {day} deleted successfully"}, status=status.HTTP_200_OK)
        elif division is not None:
            # Delete a specific divison's timetable
            timetables = TimeTable.objects.filter(semester=semester, division=division)
            timetables.delete()
            return Response({"status": f"Timetable for S{semester}{division} deleted successfully"}, status=status.HTTP_200_OK)
        else:
            # Delete the entire semester's timetable 
            timetables = TimeTable.objects.filter(semester=semester)
            timetables.delete()
            return Response({"status": f"Timetable for Semester :{semester} deleted successfully"}, status=status.HTTP_200_OK)
    except TimeTable.DoesNotExist:
        return Response({"status": "Timetable records not found"}, status=status.HTTP_404_NOT_FOUND)
    
    


def AutoTimeTableSystem(request):
    
    dayOfTheWeek = datetime.now().isoweekday()

    timetable_times={"firsttime":"firstcode",
                     "secondtime":"secondcode",
                     "thirdtime":"thirdcode",
                     "fourthtime":"fourthcode",
                     "fifthtime":"fifthcode",
                     "sixthtime":"sixthcode"}
    
    timetable_records=TimeTable.objects.all()

    for i in range(len(timetable_records)):

        serializer=TimeTableSerializer(timetable_records[i])
        for field in ['firsttime', 'secondtime', 'thirdtime', 'fourthtime', 'fifthtime', 'sixthtime']:

            starttime=serializer.data[field].split("-")[0]
            tabletime=datetime.strptime(starttime,"%I:%M %p").time().strftime("%H:%M")
            currenttime=datetime.now().time().strftime("%H:%M")

            if (currenttime=="12:00" and dayOfTheWeek!=5) or (currenttime in ['12:30',"10:40"] and dayOfTheWeek==5):
                timetable_records[i].currentcode="BREAK"

            elif (datetime.strptime(currenttime,"%H:%M").time()>=time(16,0,0,0) and dayOfTheWeek==timetable_records[i].day):
                if (dayOfTheWeek==5):
                    timetable_records[i].currentcode=TimeTable.objects.filter(day=1,semester=timetable_records[i].semester,division=timetable_records[i].division)[0].firstcode
                else:
                    timetable_records[i].currentcode=TimeTable.objects.filter(day=dayOfTheWeek+1,semester=timetable_records[i].semester,division=timetable_records[i].division)[0].firstcode
            
            elif (tabletime==currenttime) and (serializer.data["day"]==dayOfTheWeek):
                timetable_records[i].currentcode=serializer.data[timetable_times[field]]
                timetable_records[i].currenttime=currenttime

            timetable_records[i].save()



        