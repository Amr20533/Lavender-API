from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import date
from .models import Quote
from .serializers import QuoteSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quote(request):
    parser_classes = (MultiPartParser, FormParser)
    serializer = QuoteSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Quote created successfully.",
            "quote": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def daily_quote(request):
    quotes = Quote.objects.order_by('id') 
    count = quotes.count()
    
    if count == 0:
        return Response({
            "status": "error",
            "message": "No quotes found."
        }, status=404)

    index = date.today().toordinal() % count
    quote = quotes[index] 

    serializer = QuoteSerializer(quote)
    return Response({
        "status": "success",
        "quote": serializer.data
    })
