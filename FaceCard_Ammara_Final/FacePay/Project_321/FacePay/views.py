from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout
from .models import Student, FaceEmbedding, Preference, User, Transaction
from .face_recognition import save_face_embedding
import logging
from .face_recognition import recognize_face
from .models import Product, Allergy, StudentAllergy
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from django.db import transaction


# Home View
def home(request):
    return render(request, 'index.html')

# Homepage View
def homepage(request):
    return render(request, 'homepage.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        try:
            user = User.objects.get(username=username)

            if check_password(password, user.password_hash):
                # store user session
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['role'] = user.role

                # redirect based on role
                if user.role.lower() == role.lower():
                    return redirect('parent' if role == 'parent' else 'workpanel')

                messages.error(request, "Incorrect role selection!")
            else:
                messages.error(request, "Invalid username or password!")

        except User.DoesNotExist:
            messages.error(request, "User does not exist!")

    return render(request, 'login.html')


# Parent Dashboard View
def parent(request):
    user_id = request.session.get('user_id')

    if not user_id:
        print("No user session found. Redirecting to login.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        children = Student.objects.filter(parent=user)
        transactions = Transaction.objects.filter(student__parent=user).order_by("-transaction_date")

        return render(request, 'parent.html', {
            'user': user,
            'children': children,
            'transactions': transactions
        })
    except User.DoesNotExist:
        return redirect('login')


@csrf_exempt
def recharge_wallet(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount = Decimal(data.get("amount"))

            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({"success": False, "error": "User not logged in"})

            user = User.objects.get(id=user_id)
            user.wallet_balance += amount
            user.save()

            return JsonResponse({"success": True, "new_balance": str(user.wallet_balance)})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})



# POS View (Worker Role)
def pos_view(request):
    if 'user_id' not in request.session or request.session.get('role') != 'worker':
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    products = Product.objects.all()

    return render(request, 'pos.html', {'user': user, 'products': products})


# Work Panel View
def workpanel_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    return render(request, 'workpanel.html', {'user': user})



# Add Kid View
def addkid(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        student_id = request.POST.get('StudentID')
        age = request.POST.get('age')
        allergy_names = request.POST.getlist('allergies')

        parent = User.objects.get(id=request.session.get('user_id'))

        student = Student.objects.create(
            parent=parent,
            full_name=name,
            age=age
        )

        # save allergies
        for name in allergy_names:
            allergy_obj, created = Allergy.objects.get_or_create(allergy_name=name)
            StudentAllergy.objects.create(student=student, allergy=allergy_obj)


            # handle multiple custom allergies
            custom_allergies = request.POST.get('other_allergies', '').strip()
            if custom_allergies:
                for allergy_name in [a.strip() for a in custom_allergies.split(',') if a.strip()]:
                    allergy_obj, created = Allergy.objects.get_or_create(allergy_name=allergy_name)
                    StudentAllergy.objects.create(student=student, allergy=allergy_obj)


        request.session['last_added_student_id'] = student.id

        return redirect('scan_face')

    allergies = Allergy.objects.all()
    return render(request, 'addkid.html', {'allergies': allergies})


# Scan Face View
logger = logging.getLogger(__name__)

def scan_face(request):
    if request.method == 'POST':
        student_id = request.session.get('last_added_student_id')

        if not student_id:
            logger.error("No student found in session. Redirecting to addkid.")
            return JsonResponse({"success": False, "error": "No student found. Add the student first!"})

        logger.info(f"Scanning face for student ID: {student_id}")

        success = save_face_embedding(student_id)

        if success:
            logger.info(f"Face embedding successfully saved for student {student_id}. Redirecting to parent dashboard.")
            return redirect('parent')
        else:
            logger.error(f"Face embedding failed for student {student_id}. Staying on scan page.")
            return JsonResponse({"success": False, "error": "Face embedding failed!"})

    logger.warning("Invalid request to scan_face page.")
    return render(request, 'scan_face.html')

# Worker Login View
def clogin_view(request):
    return render(request, 'clogin.html')

# Canteen View
def canteen_view(request):
    return render(request, 'canteen.html')


# Registration View
def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        age = request.POST.get('age')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')

        # validate all fields are filled
        if not all([first_name, last_name, username, email, password, confirm_password, user_type]):
            messages.error(request, "All fields are required.")
            return redirect('register')

        # validate password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # validate unique username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return redirect('register')

        # validate unique email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered. Try logging in.")
            return redirect('register')

        # hash password before storing
        hashed_password = make_password(password)


        user = User.objects.create(
            full_name=f"{first_name} {last_name}",
            username=username,
            email=email,
            password_hash=hashed_password,
            role=user_type
        )

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


# Logout View
def logout_view(request):
    logout(request)
    return redirect("homepage")


# POS Scan
def scan_face_for_pos(request):
    if request.method == 'POST':
        image = recognize_face()

        if image is None:
            return JsonResponse({"success": False, "error": "Face not recognized."})


        student = FaceEmbedding.objects.filter(embedding=image).first()

        if student:
            child = student.student
            parent = child.parent

            return JsonResponse({
                "success": True,
                "child_name": child.full_name,
                "wallet_balance": child.wallet_balance,
                "parent_phone": parent.phone,
                "allergies": child.allergies or "None"
            })
        else:
            return JsonResponse({"success": False, "error": "No match found."})

    return JsonResponse({"success": False, "error": "Invalid request."})


def scan_customer_face(request):
    student, error = recognize_face()

    if error:
        return JsonResponse({"success": False, "error": error})

    print(" Scanned Student:", student.full_name, "| ID:", student.id)

    allergies = ", ".join([a.allergy_name for a in Allergy.objects.filter(studentallergy__student=student)]) or "None"

    return JsonResponse({
        "success": True,
        "student_id": student.id,
        "name": student.full_name,
        "wallet": student.parent.wallet_balance,
        "allergies": allergies,
        "allergy_list": [a.allergy.allergy_name.lower() for a in student.studentallergy_set.all()]

    })


def proceed_to_payment(request):
    if request.method == "POST":
        try:
            print(" Payment request received!")  # debugging
            data = json.loads(request.body)
            print(" Request Data:", data)

            student_id = data.get("student_id")

            if not student_id:
                return JsonResponse({"success": False, "error": "Missing student ID."})

            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({"success": False, "error": "Student not found."})

            cart_items = data.get("items")


            if not cart_items or not isinstance(cart_items, list):
                print(" cart_items is invalid:", cart_items)
                return JsonResponse({"success": False, "error": "Invalid cart data."})

            total_price = sum(item["price"] for item in cart_items)


            student = Student.objects.get(id=student_id)
            parent = student.parent


            parent.wallet_balance -= total_price
            parent.save()


            with transaction.atomic():
                Transaction.objects.create(
                    student=student,
                    cart_details=cart_items,
                    total_price=total_price
                )

            print(f" Payment successful! New balance: {parent.wallet_balance}")
            return JsonResponse({"success": True, "new_balance": float(parent.wallet_balance)})

        except Student.DoesNotExist:
            print(" Student not found!")
            return JsonResponse({"success": False, "error": "Student not found."})

        except Exception as e:
            print(" Unexpected error:", str(e))
            return JsonResponse({"success": False, "error": str(e)})

    print(" Invalid request method")
    return JsonResponse({"success": False, "error": "Invalid request."})

