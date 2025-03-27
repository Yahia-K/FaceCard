from django.db import models
from django.contrib.auth.models import User
import json
from django.utils import timezone

class User(models.Model):
    ROLE_CHOICES = [
        ('parent', 'Parent'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    ]
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Student(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    student_photo = models.CharField(max_length=255, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

class FacialRecognitionData(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    face_encoding = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

class Item(models.Model):
    item_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, null=True, blank=True)
    available_stock = models.IntegerField(default=0)

class Preference(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    allergy_info = models.TextField(null=True, blank=True)
    daily_spending_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Allergy(models.Model):
    allergy_name = models.CharField(max_length=255, unique=True)

class StudentAllergy(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    allergy = models.ForeignKey(Allergy, on_delete=models.CASCADE)

class ItemAllergy(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    allergy = models.ForeignKey(Allergy, on_delete=models.CASCADE)

class POSTerminal(models.Model):
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')


class Transaction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    cart_details = models.JSONField(default=dict)
    transaction_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)


class PaymentMethod(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=[('Credit Card', 'Credit Card'), ('PayPal', 'PayPal'), ('Stripe', 'Stripe')])
    payment_details = models.CharField(max_length=255)

class FaceEmbedding(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    embedding = models.TextField()

    def set_embedding(self, embedding_array):
        #convert numpy array to json and store
        self.embedding = json.dumps(embedding_array.tolist())

    def get_embedding(self):
        #retrieve embedding as numpy array
        return json.loads(self.embedding)


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ingredients = models.TextField()

    def __str__(self):
        return self.name

