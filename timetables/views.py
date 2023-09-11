from django.shortcuts import render
from rest_framework.decorators import api_view
import pandas as pd
from .serializers import TimeTableSerializer
from rest_framework.response import Response
from rest_framework import status

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
                data['firsttime']='9-9:50'
                data['secondtime']='9:50-10:40'
                data['thirdtime']='10:50-11:40'
                data['fourthtime']='11:40-12:30'
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
            serializer_instance.firsttime='9-9:50'
            serializer_instance.secondtime='9:50-10:40'
            serializer_instance.thirdtime='10:50-11:40'
            serializer_instance.fourthtime='11:40-12:30'
            
        serializer_instance.save()
        
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


    


            

