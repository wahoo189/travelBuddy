from django.shortcuts import render, redirect
from .models import User, Trip, Trip_Join
import re, datetime, bcrypt
from django.contrib import messages
from django.http import HttpResponseRedirect

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
PASSWORD_CAP_DIG_REGEX = re.compile(r'\d+.*[A-Z]+|[A-Z]+.*\d+')
LOGGED_IN_USER_ID = "LOGGED_IN_USER_ID"
APP_NAME = 'TravelBuddyApp'

# Create your views here.
def main(request):
    return render(request, APP_NAME+'/main.html')

def login(request):
    try:
        if len(request.POST['userName']) < 1 or len(request.POST['password']) < 1:
            messages.add_message(request, messages.INFO, 'Username and Password cannot be blank!')
            return redirect('/')

        print "ATTEMPTING TO LOG IN THIS USER: ", request.POST['userName']
        user = User.objects.get(username=request.POST['userName'])

        if bcrypt.hashpw(request.POST['password'].encode(), user.password.encode()) == user.password.encode():
            request.session[LOGGED_IN_USER_ID] = user.id
            return redirect('/travels')
        else:
            messages.add_message(request, messages.INFO, 'Incorrect Password!')
            return redirect('/')
    except Exception as ex:
        messages.add_message(request, messages.INFO, ex)
        return redirect('/')

def logout(request):
    request.session[LOGGED_IN_USER_ID] = 0
    return redirect('/')

def register(request):
    if tryCreateUser(request):
        return login(request)
    else:
        messages.add_message(request, messages.INFO, 'An error occurred, please try again.')
        return redirect('/')

def travels(request):
    availableTrips = []

    try:
        user = User.objects.get(id=request.session[LOGGED_IN_USER_ID])
        query = 'SELECT * FROM "TravelBuddyApp_trip" WHERE user_id != ' + str(user.id) + ' and id not in (SELECT trip_id from "TravelBuddyApp_trip_join" where attendee_id = ' + str(user.id) + ' )'
        availableTrips = Trip.objects.raw(query)
    except Exception,e:
        pass # if no trips are available, that's ok.

    context = {
        "User" : user,
        "Trips" : Trip.objects.filter(user=user),
        "Attending" : Trip_Join.objects.filter(attendee=user)
        , "OthersTrips" : availableTrips
    }
    return render(request, APP_NAME+'/travels.html', context)

def join(request, id):
    user = User.objects.get(id=request.session[LOGGED_IN_USER_ID])
    trip = Trip.objects.get(id=id)
    Trip_Join.objects.create(trip=trip, attendee=user)

    messages.add_message(request, messages.INFO, 'You are joining trip ' + str(id))
    return redirect('/travels')

def add(request):
    return render(request, APP_NAME+'/add.html')

def addTravel(request):
    for field in request.POST:
		#if field.type == "TextField":
        if len(request.POST[field]) < 1:
            print("All fields are required!")
            messages.add_message(request, messages.INFO, 'All fields are required!')
            # errorsExist = True
            return redirect("/add")
            break
    try:
        startDate = datetime.datetime.strptime(request.POST['start_date'],'%m/%d/%Y')
        endDate = datetime.datetime.strptime(request.POST['end_date'],'%m/%d/%Y')

        if startDate < datetime.datetime.now():
            messages.add_message(request, messages.INFO, 'Start Date must be after today')
            return redirect("/add")
        elif startDate > endDate:
            messages.add_message(request, messages.INFO, 'End Date must be after Start Date')
            return redirect("/add")
    except Exception,e:
        messages.add_message(request, messages.INFO, 'The dates entered are invalid.')
        return redirect("/add")


    user = User.objects.get(id=request.session[LOGGED_IN_USER_ID])
    print "Destination: ", request.POST['destination']
    Trip.objects.create(user=user, destination=request.POST['destination'], start_date=startDate, end_date=endDate, plan=request.POST['description'])
    return redirect('/travels')

def tripDetail(request, id):
    attendees = None
    try:
        attendees = Trip_Join.objects.filter(trip=id)#.exclude(attendee=user)
    except:
        pass

    context = {
        "trip" : Trip.objects.get(id=id),
        "attendees" : attendees
        }
    return render(request, APP_NAME+'/tripDetail.html', context)

def listUsers(request):
    context = {"Users" : User.objects.all()}
    return render(request, APP_NAME+'/listUsers.html', context)

def listAttendees(request):
    context = {"Attendees" : Trip_Join.objects.all()}
    return render(request, APP_NAME+'/listAttendees.html', context)

# ===================
# INTERNAL FUNCTIONS:
# ===================

def tryCreateUser(request):
    if registrationValidation(request):
        print "VALIDATION PASSED FOR USER: ", request.POST['userName']
        if User.objects.filter(username=request.POST['userName']).count() == 0:
            newUser = {}
            print ("ATTEMPTING TO REGISTER USER")

            bcryptedPW = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())

            if User.objects.all().count() == 0: # Make first user an admin.
                accessLevel = "ADMIN"
            else:
                accessLevel = "NORMAL"

            newUser = User.objects.create(name=request.POST['name'], username=request.POST['userName'], password=bcryptedPW)

            return True

        else:
            print ("USER ALREADY EXISTS: ", request.POST['userName'])
            messages.add_message(request, messages.INFO, 'User already exists!')
            return False
    else:
        print ("REGISTRATION FAILED FOR USER: ", request.POST['userName'])
        messages.add_message(request, messages.INFO, 'Registration failed for user ' + request.POST['userName'])
        return False

def validatePassword(request, password, password_confirm):
    errorsExist = False
    # Password should be more than 8 characters
    if len(password) < 8:
        messages.add_message(request, messages.INFO, 'Passwords must contain at least 8 characters!')
        print("Password must contain at least 8 characters!")
        errorsExist = True
    # Password and Password Confirmation should match
    if password != password_confirm :
        messages.add_message(request, messages.INFO, 'Passwords do not match!')
        print("Passwords do not match!")
        errorsExist = True
    # Password to have at least 1 uppercase letter and 1 numeric value.
    if not PASSWORD_CAP_DIG_REGEX.match(password):
        errorsExist = True
        messages.add_message(request, messages.INFO, 'Password must contain at least 1 upper case letter and 1 numeric value')
        print("Password must contain at least 1 upper case letter and 1 numeric value")

    return not errorsExist

def registrationValidation(request):
    errorsExist = False
    try:
        # All fields are required and must not be blank
    	for field in request.POST:
    		#if field.type == "TextField":
            if len(request.POST[field]) < 1:
                print("All fields are required!")
                messages.add_message(request, messages.INFO, 'All fields are required!')
                errorsExist = True
                break

    # First and Last Name cannot contain any numbers
    	if any(char.isdigit() for char in request.POST['name']):
            messages.add_message(request, messages.INFO, 'Name values cannot contain numbers!')
            print("Name values cannot contain numbers!")
            errorsExist = True

        if not validatePassword(request, request.POST['password'], request.POST['passwordConfirm']):
            errorsExist = True

    # No errors?
    	if not errorsExist:
            messages.add_message(request, messages.INFO, "Thanks for submitting your information.")
            print("Thanks for submitting your information.")

    except Exception,e:
        print "ERROR: ", str(e)

    return not errorsExist
