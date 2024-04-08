from .models import TimeTable
from datetime import datetime, time
from .serializers import TimeTableSerializer
from celery import shared_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

def is_within_range(time_str, start_time_str, end_time_str):
    time = datetime.strptime(time_str, "%H:%M")
    start_time = datetime.strptime(start_time_str, "%H:%M")
    end_time = datetime.strptime(end_time_str, "%H:%M")
    return start_time <= time <= end_time

class AutoTimeTableSystem(APIView):
    
    # permission_classes = (IsAuthenticated,)
    
    
    def post(self,request):
        
        try:
            dayOfTheWeek = datetime.now().isoweekday()
            
            print("Day of the week: ",dayOfTheWeek)
            timetable_times={"firsttime":"firstcode",
                            "secondtime":"secondcode",
                            "thirdtime":"thirdcode",
                            "fourthtime":"fourthcode",
                            "fifthtime":"fifthcode",
                            "sixthtime":"sixthcode"}
            
            if dayOfTheWeek in [6,7]:
                dayOfTheWeek=1
                
                timetable_records=TimeTable.objects.filter(day=dayOfTheWeek).all()
                
                for i in range(len(timetable_records)):
                    serializer = TimeTableSerializer(timetable_records[i])
                    
                    starttime=serializer.data["firsttime"].split("-")[0]
                    tabletime=datetime.strptime(starttime,"%I:%M %p").time().strftime("%H:%M")
                    
                    print('firstcode ',serializer.data["firstcode"])
                    timetable_records[i].currentcode=serializer.data["firstcode"]
                    timetable_records[i].currenttime=starttime
                    
                    timetable_records[i].save()
                    
                    
            else:
                timetable_records=TimeTable.objects.filter(day=dayOfTheWeek).all()
                
                print("timetable_records: ",timetable_records)
                
                for i in range(len(timetable_records)):

                    serializer=TimeTableSerializer(timetable_records[i])
                    for field in ['firsttime', 'secondtime', 'thirdtime', 'fourthtime', 'fifthtime', 'sixthtime']:

                        starttime=serializer.data[field].split("-")[0]
                        tabletime=datetime.strptime(starttime,"%I:%M %p").time().strftime("%H:%M")
                        
                        endtime=serializer.data[field].split("-")[1]
                        endtabletime=datetime.strptime(endtime,"%I:%M %p").time().strftime("%H:%M")
                        currenttime=datetime.now().time().strftime("%H:%M")

                        if (is_within_range(currenttime, '12:00', '13:00') and dayOfTheWeek!=5) or (is_within_range(currenttime, '10:30', '10:50') and is_within_range(currenttime, '12:30', '14:00') and dayOfTheWeek==5):
                            timetable_records[i].currentcode="BREAK"
                            
                            timetable_records[i].currenttime="12:00 PM"
                            
                            timetable_records[i].save()
                            
                            print(currenttime, starttime, endtime)
                            break

                        elif (datetime.strptime(currenttime,"%H:%M").time()>=time(16,0,0,0) and dayOfTheWeek==timetable_records[i].day):
                            if (dayOfTheWeek==5):
                                timetable_records[i].currentcode=TimeTable.objects.filter(day=1,semester=timetable_records[i].semester,division=timetable_records[i].division)[0].firstcode
                                
                            else:
                                timetable_records[i].currentcode=TimeTable.objects.filter(day=dayOfTheWeek+1,semester=timetable_records[i].semester,division=timetable_records[i].division)[0].firstcode
                                
                            timetable_records[i].currenttime=starttime
                            
                            timetable_records[i].save()
                            
                            print("After class on the same day")
                            
                            break
                        
                        elif (is_within_range(currenttime, tabletime, endtabletime)) and (serializer.data["day"]==dayOfTheWeek):
                            timetable_records[i].currentcode=serializer.data[timetable_times[field]]
                            
                            timetable_records[i].currenttime=starttime

                            timetable_records[i].save()
                            
                            print("During class")
                            
                            break
                        
            return Response({'status':'success'},status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'status':'failed'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)           
            
        
                

                
         
