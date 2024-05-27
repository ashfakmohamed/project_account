# views.py
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests

class AccountListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationListCreateView(generics.ListCreateAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

class DestinationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

class Api(APIView):
    def get(self,request):
        datas = {"ashfak":"core","data":"file"}
        return Response({"result":datas})

    def post(self,request):
        # datas = request.get('json')
        return Response({"result":request})


@api_view(['POST'])
def incoming_data(request):
    if 'CL-X-TOKEN' not in request.headers:
        return Response({'error': 'Unauthenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    app_secret_token = request.headers['CL-X-TOKEN']
    
    try:
        account = Account.objects.get(app_secret_token=app_secret_token)
    except Account.DoesNotExist:
        return Response({'error': 'Invalid app secret token'}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data
    http_method = data.get('http_method', 'GET').upper()
    
    if not isinstance(data, dict):
        return Response({'error': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)

    destinations = Destination.objects.filter(account=account)

    for destination in destinations:
        url = destination.url
        headers = destination.headers

        try:
            if http_method == 'POST':
                response = requests.post(url, json=data, headers=headers)
                return Response({'Message': response }, status=status.HTTP_200_OK)
            else:
                return Response({'error': f'Unsupported HTTP method: {http_method}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Error sending data to {url}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'Message':"success" }, status=status.HTTP_200_OK)