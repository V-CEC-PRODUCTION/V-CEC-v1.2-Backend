from .models import TimeTable
from datetime import datetime, time
from .serializers import TimeTableSerializer
from celery import shared_task
from timetables.consumers import TimeTableConsumer

@shared_task
def AutoTimeTableSystem():
    
    dayOfTheWeek = datetime.now().isoweekday()
    
    print("Day of the week: ",dayOfTheWeek)
    timetable_times={"firsttime":"firstcode",
                     "secondtime":"secondcode",
                     "thirdtime":"thirdcode",
                     "fourthtime":"fourthcode",
                     "fifthtime":"fifthcode",
                     "sixthtime":"sixthcode"}
    
    if dayOfTheWeek in [6,7]:
        dayOfTheWeek=5
    
    timetable_records=TimeTable.objects.filter(day=dayOfTheWeek).all()
    

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
            timetable_records[i].currenttime=starttime

            timetable_records[i].save()
            
            team_score_update = TimeTableConsumer()
            
            team_score_update.cur_subject_and_time_changed(instance=timetable_records[i])  
