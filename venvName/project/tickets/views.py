from django.http import Http404
from django.shortcuts import render
from django.http.response import JsonResponse 
from .models import Guest, Movie, Reservation, Post
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import GuestSerializer , MovieSerializer , ReservationSerializer, PostSerializer
from rest_framework import status, filters
from rest_framework.decorators import permission_classes
from rest_framework import permissions , generics , mixins , viewsets
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly
# Create your views here.

#1 without REST & no Models Query FBV
def no_rest_no_model(request):
    guest =[
        {
            'id':1,
            "Name":"Ahmed",
            "mobile":789582,
        },
        {
            'id':2,
            "Name":"Omar",
            "mobile":723662,
        }
    ]
    return JsonResponse(guest, safe=False)

#2 model data default without rest
def no_rest_from_model(request):
    data = Guest.objects.all()
    response = {
        "guests": list(data.values('name','mobile'))
    }
    return JsonResponse(response)

# List ==> GET
# Create ==> POST
# pk Query ==> GET
# Update == PUT
# Delete destroy == DELETE 

#3 Function based views
#3.1 GET POST
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def FBV_List(request):
    
    # GET
    if request.method == 'GET':
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)
    # POST   
    elif request.method == 'POST':
        serializer = GuestSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        return Response(serializer.data , status=status.HTTP_400_BAD_REQUEST)
             


#3.1 GET PUT DELETE
@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def FBV_pk(request,pk):
    try:
        guest = Guest.objects.get(pk= pk)
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # GET
    if request.method == 'GET':
        serializer = GuestSerializer(guest)
        return Response(serializer.data)
    # PUT   
    elif request.method == 'PUT':
        serializer = GuestSerializer(guest, data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_200_OK)
        return Response(serializer.data , status=status.HTTP_400_BAD_REQUEST)
    # DELETE
    if request.method == 'DELETE':
        guest.delete()
        return Response(status= status.HTTP_204_NO_CONTENT)


# CBV Class based views
#4.1 List and Create == GET & POST
@permission_classes([IsAuthenticated])
class CBV_List(APIView):
    def get(self, request):
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many = True)
        return Response(serializer.data)
    def post(self, request):
        serializer = GuestSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


#4.2 GET PUT DELETE class based views -- pk
@permission_classes([IsAuthenticated])
class CBV_pk(APIView):
    def get_objects(self, pk):
        try:
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExist:
            raise Http404
    def get(self, request, pk):
        guest = self.get_objects(pk)
        serializer= GuestSerializer(guest)
        return Response(serializer.data)
    
    def put(self, request, pk):
        guest = self.get_objects(pk)
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        guest = self.get_objects(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

#5 Mixins  
#5.1 mixins list   GET & POST
class mixins_list(mixins.ListModelMixin , mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    
    def get(self, request):
        return self.list(request)
    
    def post(self, request):
        return self.create(request)
          
#5.2 mixins GET PUT DELETE
class mixins_pk(mixins.RetrieveModelMixin , mixins.UpdateModelMixin , mixins.DestroyModelMixin , generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    
    def get(self, request, pk):
        return self.retrieve(request)
    
    def put(self, request, pk):
        return self.update(request)
    
    def delete(self, request, pk):
        return self.destroy(request)
    
  
#6 Genaric
#6.1 GET & POST
class generic_list(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]

#6.2 GET POST & DELETE
class generic_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]
    
#7 viewsets
class viewsets_guest(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    
class viewsets_movie(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backend = [filters.SearchFilter]
    search_fields = ['movie']
    
class viewsets_reservation(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = ReservationSerializer
    
#8 Find movie 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_movie(request):
    movies = Movie.objects.filter(
        #hall = request.data['hall'],
        #movie = request.data['movie'],
    )
    serializer = MovieSerializer(movies, many= True)
    return Response(serializer.data)

#9 create new reservation
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_reservation(request):
    movie = Movie.objects.get(hall = request.data['hall'] , movie = request.data['movie'])
    guest = Guest()
    guest.name = request.data['name']
    guest.mobile = request.data['mobile']
    guest.save()
    
    reservation = Reservation()
    reservation.guest = guest
    reservation.movie = movie
    reservation.save()
    serializer = ReservationSerializer(reservation)
    return Response(serializer.data,status=status.HTTP_201_CREATED)
    

#10 POST author editor
class Post_pk(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthorOrReadOnly]
    queryset = Post.objects.all()
    serializer_class = PostSerializer()