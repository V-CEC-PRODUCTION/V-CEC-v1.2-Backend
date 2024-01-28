from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import staffInfo
from .serializers import StaffSerializer
from django.core.exceptions import ObjectDoesNotExist  
from django.core.cache import cache
import json
from vcec_bk.pagination import CustomPageNumberPagination


class full_staff_search(APIView,CustomPageNumberPagination):
    def get(self,request,search):
        try:

            #search = request.GET.get('search')
            print("Search term:", search)
            
            queryset = staffInfo.objects.all()
            
            if search:
                print("Before filtering, total objects:", queryset.count())
                
                queryset = queryset.filter(name__icontains=search)
                print("After filtering, objects matching search:", queryset.count())
                
                results_search = self.paginate_queryset(queryset, request)
                serializer = StaffSerializer(results_search, many=True)
                
                response = {
                    "staff_info": serializer.data,
                    "has_next": self.page.has_next(),
                    "has_previous": self.page.has_previous(),
                    "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
                    "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,
                }
                
                return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

class search_staff_dep(APIView,CustomPageNumberPagination):
    def get(self,request,dep):
        try:

            search = request.GET.get('search')
            
            staff_dir = staffInfo.objects.filter(department=dep)
            
            queryset = staff_dir.filter(name__icontains=search) 
            
            results_search = self.paginate_queryset(queryset, request)
            
            serializer = StaffSerializer(results_search, many=True)
            
            response = {
                "staff_info": serializer.data,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "next_page_number": self.page.next_page_number() if self.page.has_next() else None,
                "previous_page_number": self.page.previous_page_number() if self.page.has_previous() else None,
            }
                
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# class staff_dep(APIView,CustomPageNumberPagination):
#     def get(self,request,dep):
#         try:   
#             page_number = request.GET.get('page')
#             page_count = request.GET.get('count')
            
#             if page_number is None:
#                 page_number = 1
            
#             if page_count is None:
#                 page_count = 1
                
#             dep_name = f"{dep}_{page_number}_{page_count}"
            
#             dep_result = cache.get(dep_name)
            
#             if dep_result is None:
#                 print("Data from database")
#                 staff_dir = staffInfo.objects.filter(department=dep)
                
#                 results = self.paginate_queryset(staff_dir, request)
            
#                 serializer = StaffSerializer(results, many=True)
                
#                 dep_result = {
#                     'data': serializer.data,
#                     'has_next': self.page.has_next(),
#                     'has_previous': self.page.has_previous(),
#                     'next_page_number': self.page.next_page_number() if self.page.has_next() else None,
#                     'previous_page_number': self.page.previous_page_number() if self.page.has_previous() else None,
#                 }
                
#                 cache.set(dep_name, json.dumps(dep_result),timeout=60*60*24*7)
                
#             else:
#                 print("Data from cache")
#                 dep_result = json.loads(dep_result)
                
            
#             response = {
#                 "staff_info": dep_result['data'],
#                 "has_next": dep_result['has_next'],
#                 "has_previous": dep_result['has_previous'],
#                 "next_page_number": dep_result['next_page_number'],
#                 "previous_page_number": dep_result['previous_page_number'],
#             }
            
#             return Response(response, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
class staff_list(APIView,CustomPageNumberPagination):
    def get(self,request):
        
        page_number = request.GET.get('page')
        page_count = request.GET.get('count')
        
        if page_number is None:
            page_number = 1
        
        if page_count is None:
            page_count = 1
            
        dep_name = f"all_staff_{page_number}_{page_count}"  
        dep_result = cache.get(dep_name)
        
        # dep_result = None
                    
        if dep_result is None:
            print("Data from database")
                 
            results = self.paginate_queryset(staffInfo.objects.all(), request)
            
            serializer = StaffSerializer(results, many=True)
            
            dep_result = {
                'data': serializer.data,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next_page_number': self.page.next_page_number() if self.page.has_next() else None,
                'previous_page_number': self.page.previous_page_number() if self.page.has_previous() else None,
            }
            
            cache.set(dep_name, json.dumps(dep_result),timeout=60*60*24*7)
        else:
            print("Data from cache")
            dep_result = json.loads(dep_result)
        
        response = {
            "staff_info": dep_result['data'],
            "has_next": dep_result['has_next'],
            "has_previous": dep_result['has_previous'],
            "next_page_number": dep_result['next_page_number'],
            "previous_page_number": dep_result['previous_page_number'],
        }
        
        return Response(response)

    def post(self,request):
        serializer = StaffSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
    
            for dep_name in ['CSE*','EEE*','ECE*','GE*','BSL*','LIB*','all_staff*']:        
                cache.delete_pattern(dep_name)
                
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
            
            for dep_name in ['CSE*','EEE*','ECE*','GE*','BSL*','LIB*','all_staff*']:        
                cache.delete_pattern(dep_name)
                
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        
@api_view(['DELETE'])
def staff_delete(request,pk):   
    if request.method == 'DELETE':
        try:
            info = staffInfo.objects.get(pk=pk)
            
            info.delete()
            
            for dep_name in ['CSE*','EEE*','ECE*','GE*','BSL*','LIB*','all_staff*']:        
                cache.delete_pattern(dep_name)
                
            return Response({"message": "Staff info removed from the database"}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response("Staff does not exist!", status=status.HTTP_404_NOT_FOUND)
    