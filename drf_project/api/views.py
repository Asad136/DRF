from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
import csv
from django.http import HttpResponse
from rest_framework_simplejwt.exceptions import InvalidToken

@api_view(['POST'])
def signup(request):
    person = UserSerializer(data=request.data)
    if person.is_valid():
        person.save()
        return Response(person.data, status=status.HTTP_201_CREATED)
    return Response(person.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def loginuser(request):
    try:
        user = User.objects.get(username=request.data['username'])
        if user.check_password(request.data['password']):
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def productlist(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    is_superuser = request.user.is_superuser
    response_data = {
            'is_superuser': is_superuser,
            'products': serializer.data
        }
    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def productcreate(request):
    if request.user.is_superuser:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Only superusers can create products'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def productdetail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product)
    return Response(serializer.data)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def productupdate(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_superuser:
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Only superusers can edit products'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def productdelete(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_superuser:
        product.delete()
        return Response({'message: this product is deleted'},status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({'error': 'Only superusers can delete products'}, status=status.HTTP_403_FORBIDDEN)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def downloadcsv(request):
    if not request.user.is_superuser:
        return Response({'error': 'Only superusers can download CSV'}, status=status.HTTP_403_FORBIDDEN)

    response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="myfile.csv"'},
        )

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Description', 'Price', 'Created At', 'Updated At'])

    products = Product.objects.all()
    for product in products:
        writer.writerow([product.id, product.name, product.description, product.price, product.created_at, product.updated_at])

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
    except InvalidToken:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)