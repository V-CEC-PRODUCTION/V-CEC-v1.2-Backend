from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import staffInfo
from .serializers import StaffSerializer
from django.core.exceptions import ObjectDoesNotExist  

@api_view(['GET'])
def full_staff_search(request,search):
    try:
        if request.method == 'GET':
            
            #search = request.GET.get('search')
            print("Search term:", search)
            
            queryset = staffInfo.objects.all()
            
            if search:
                print("Before filtering, total objects:", queryset.count())
                
                queryset = queryset.filter(name__icontains=search)
                print("After filtering, objects matching search:", queryset.count())
            
                serializer = StaffSerializer(queryset, many=True)
                
                response = {
                    "staff_info": serializer.data
                }
                
                return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['GET'])
def search_staff_dep(request,dep):
    try:
        if request.method == 'GET':
            
            search = request.GET.get('search')
            
            staff_dir = staffInfo.objects.filter(department=dep)
            
            queryset = staff_dir.filter(name__icontains=search) 
            
            serializer = StaffSerializer(queryset, many=True)
            
            response = {
                "staff_info": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def staff_dep(request,dep):
    try:
        if request.method == 'GET':
            staff_dir = staffInfo.objects.filter(department=dep)
            serializer = StaffSerializer(staff_dir, many=True)
            
            response = {
                "staff_info": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    
@api_view(['GET', 'POST'])
def staff_list(request):
    if request.method == 'GET':
        staff_dir = staffInfo.objects.all()
        serializer = StaffSerializer(staff_dir, many=True)
        
        response = {
            "staff_info": serializer.data
        }
        return Response(response)
    
    elif request.method == 'POST':
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def staff_detail(request, pk):
    try:
        info = staffInfo.objects.get(pk=pk)
    except staffInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'GET':
        serializer = StaffSerializer(info)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = StaffSerializer(info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            info.delete()
            return Response({"message": "Staff info removed from the database"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['DELETE'])
def staff_delete(request,pk):   
    if request.method == 'DELETE':
        try:
            info = staffInfo.objects.get(pk=pk)
            
            info.delete()
            
            return Response({"message": "Staff info removed from the database"}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response("Staff does not exist!", status=status.HTTP_404_NOT_FOUND)
    