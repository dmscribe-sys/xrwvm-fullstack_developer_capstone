# DMSCRIBE UNCOMMENT 

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review
# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

#DMSCRIBE ADD
# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)                  # Terminates user session
    data = {"userName": ""}          # Return empty username
    return JsonResponse(data)

#DMSCRIBE ADD
# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    if User.objects.filter(username=username).exists():
        return JsonResponse({"status": "Failed", "message": "Already Registered"})

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})

# DMSCRIBE GET GETS REQUEST
def get_cars(request):
    count = CarMake.objects.filter().count()
    if count == 0:
        from .populate import initiate
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for cm in car_models:
        cars.append({
            "CarMake": cm.car_make.name,
            "CarModel": cm.name
        })
    return JsonResponse({"CarModels": cars})

# 1. Get all dealers (or by state)
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

# 2. Get dealer details by ID
def get_dealer_details(request, dealer_id):
    endpoint = f"/fetchDealer/{dealer_id}"
    dealer = get_request(endpoint)
    return JsonResponse({"status": 200, "dealer": dealer})

# 3. Get dealer reviews by ID + sentiment analysis
def get_dealer_reviews(request, dealer_id):
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)
    for review in reviews:
        response = analyze_review_sentiments(review['review'])
        review['sentiment'] = response.get('sentiment', 'unknown')
    return JsonResponse({"status": 200, "reviews": reviews})

# 4. Add a review
@csrf_exempt
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 401, "message": "Unauthorized"})

    try:
        data = json.loads(request.body)
        print("Parsed data:", data)

        post_response = post_review(data)  # Express call
        print("Response from backend:", post_response)

        # Safely return the result
        return JsonResponse(post_response, safe=False)
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return JsonResponse({"status": 500, "message": "Invalid JSON sent"})
    except Exception as e:
        print("Error in add_review:", e)
        return JsonResponse({"status": 500, "message": str(e)})
