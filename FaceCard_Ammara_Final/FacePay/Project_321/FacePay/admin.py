from django.contrib import admin
from .models import User, Student, FacialRecognitionData, Item, Preference, Allergy, StudentAllergy, ItemAllergy, POSTerminal, Transaction, PaymentMethod

admin.site.register(User)
admin.site.register(Student)
admin.site.register(FacialRecognitionData)
admin.site.register(Item)
admin.site.register(Preference)
admin.site.register(Allergy)
admin.site.register(StudentAllergy)
admin.site.register(ItemAllergy)
admin.site.register(POSTerminal)
admin.site.register(Transaction)
admin.site.register(PaymentMethod)
