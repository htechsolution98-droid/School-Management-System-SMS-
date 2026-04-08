from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializer import *
from rest_framework.permissions import BasePermission ,IsAuthenticated
import random
import string
from django.core.mail import send_mail
from django.contrib.auth.models import Group

from django.conf import settings
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from django.db.models import Q

from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your views here.
# set access and refresh token in cookie 
class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomeLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data.pop('access', None)
            refresh = response.data.pop('refresh', None)

            response.set_cookie(
                key='access_token',
                value=access,
                httponly=True,
                secure=False,  # True in production (HTTPS)
                samesite='Lax'
            )

            response.set_cookie(
                key='refresh_token',
                value=refresh,
                httponly=True,
                secure=False,
                samesite='Lax'
            )

        return response
    

from rest_framework_simplejwt.views  import TokenRefreshView

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return None
        
        request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.get('access')
            
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            
        return response
            
            
#====== CODE for GENERATE ID & CODE =====
def generate_school_code(name):
    school_name = name.split(' ')[0]
    digit = string.digits

    four_digit = ''.join(random.choices(digit,k=4))
    school_code = school_name+four_digit

    if School.objects.filter(code = school_code).exists():
        return generate_school_code(name)

    return school_code

def generate_staff_username(name):
    Staff_name = name.split(' ')[0]
    digit = string.digits

    four_digit = ''.join(random.choices(digit,k=4))
    Staff_username = Staff_name+four_digit

    if User.objects.filter(username = Staff_username).exists():
        return generate_staff_username(name)

    return Staff_username

#======END CODE for GENERATE ID & CODE =====


# =========PERMISSIONS===========
class Is_super_admin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='super_admin').exists()
    

class Is_admin_trustee(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='admin(trustee)').exists()
               
class IsCLerk(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='CLERK').exists()
               
class Isprincipal(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='PRINCIPAL').exists()
               
class Isstudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.groups.filter(name='student').exists()


from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.core.cache import cache
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

class SchoolView(ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, Is_super_admin]

    # 🔹 Get schools with cache
    def get_queryset(self):
        cache_key = "school_list"

        data = cache.get(cache_key)

        if not data:
            qs = School.objects.all()
            return qs

    # # 🔹 Override list to cache serialized data (BEST PRACTICE)
    # def list(self, request, *args, **kwargs):
    #     cache_key = "school_list"

    #     data = cache.get(cache_key)

    #     if not data:
    #         queryset = School.objects.all()
    #         serializer = self.get_serializer(queryset, many=True)
    #         data = serializer.data
    #         cache.set(cache_key, data, timeout=60 * 10)  # 10 minutes

    #     response = Response(data)
    #      # 👈 check in Postman
    #     return response

    # Create school + clear cache
    def perform_create(self, serializer):
        name = serializer.validated_data.get('name')
        school_code = generate_school_code(name)

        with transaction.atomic():
            user = User.objects.create(username=school_code)
            password = school_code
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name='admin(trustee)')
            user.groups.add(group)

            serializer.save(code=school_code, login_id=user)

        #  Clear cache after create
        cache.delete("school_list")

    # 🔹 Update + clear cache
    def perform_update(self, serializer):
        serializer.save()
        cache.delete("school_list")

    # 🔹 Delete + clear cache
    def perform_destroy(self, instance):
        instance.delete()
        cache.delete("school_list")

    # 🔹 Custom response
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({
            "message": "School created Successfully"
        }, status=201)

from django.core.cache import cache

class StaffView(ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, Is_admin_trustee]

    # 🔹 Get staff list with Redis cache
    def get_queryset(self):
        user = self.request.user
        cache_key = f"staff_list_{user.id}"

        staff_qs = cache.get(cache_key)
        if staff_qs:
            print("its form cach")

        if not staff_qs:
            staff_qs = Staff.objects.filter(school__login_id=user)
            cache.set(cache_key, staff_qs, timeout=60 * 60 * 5)  # 5 hours cache

        return staff_qs

    # 🔹 Create staff + clear cache
    def perform_create(self, serializer):
        name = serializer.validated_data.get('name')
        category = serializer.validated_data.get('category')

        group, created = Group.objects.get_or_create(name=category)

        username = generate_staff_username(name)

        user = User(username=username)
        user.set_password(username)
        user.save()

        user.groups.add(group)

        school = School.objects.filter(login_id=self.request.user).first()

        serializer.save(user=user, school=school)

        # 🔥 Clear cache after create
        cache.delete(f"staff_list_{self.request.user.id}")

    # 🔹 Update staff + clear cache
    def perform_update(self, serializer):
        serializer.save()
        cache.delete(f"staff_list_{self.request.user.id}")

    # 🔹 Delete staff + clear cache
    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(f"staff_list_{self.request.user.id}")

class StudentSignUpView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = StudentSignUpSerliazer
    
    http_method_names = ['post']
    

# =============TO ask more=========       

# class FormViewSet(ModelViewSet):
#     queryset = Form.objects.all()
#     serializer_class = FormSerializer
#     # permission_classes = [IsAuthenticated]

# class FormDetailAPIView(RetrieveAPIView):
#     queryset = Form.objects.all()
#     serializer_class = FormSerializer


# class SubmitFormView(APIView):
#     def post(self, request, id):
#         print("RAW BODY:", request.body)
#         print("PARSED DATA:", request.data)

#         form = Form.objects.get(id=id)

#         for field in form.fields.all():
#             print("Looking for key:", str(field.id))

#             value = request.data.get(str(field.id))
#             print("VALUE FOUND:", value)

#             field.value = value
#             field.save()

#         return Response({"message": "Saved"})
    
# =============end TO ask more===========


# class StudentView(ModelViewSet):
#     queryset = Student.objects.all()
#     serializer_class = StudentSerializer

#     def perform_create(self, serializer):
#         student = serializer.save()

#     # Now safely access fields from the saved instance
#         link = f"http://127.0.0.1:8000/admission?id={student.id}"

#         send_mail(
#             subject="Admission Form",
#             message=f"Fill this admission form using the link: {link}",
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[student.email],
#         )

       
# class StudentDocumentview(ModelViewSet):
#     queryset = StudentDocument.objects.all()
#     serializer_class = StudentDocumentSerializer
    
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         student_id = self.request.query_params.get('student_id')

#         if student_id:
#             queryset = queryset.filter(student_id=student_id)

#         return queryset
    

class StudentFIllView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentFIllSerilaizer


class ClerkVerifyView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = ClerkVerifySerializr
    

class PrincipleVerifyView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = PrincipleVerifySerializr
    
    def get_queryset(self):
        return Student.objects.filter(clerk_verified = True)


class FeeVerifyView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = FeesVerifySerializr
    
    def get_queryset(self):
        return Student.objects.filter(Q(clerk_verified = True) & Q(principle_verified=True))

# =====serializer for School class=====

class SchoolClassView(ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    
# ========================================
    
# ========= admissions process views ========
from rest_framework import status

class AdmissionFormViewSet(ModelViewSet):
    queryset = AdmissionForm.objects.all()
    serializer_class = AdmissionFormSerializer
    # permission_classes = [IsAuthenticated,Isprincipal]  
    
 
    lookup_field = 'unique_link'  # access form via UUID

    def get_queryset(self):
        return AdmissionForm.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        school = School.objects.get(login_id=self.request.user)
        serializer.save(school=school.id)
    
    # def create(self, request, *args, **kwargs):
    #     serializer = super().create(request, *args, **kwargs)
        
    #     return Response({
    #         "meassage":"Form created Successfully"
    #         }, status=status.HTTP_201_CREATED)
   
   
# ====this view set for view admission form field====

class FormFieldViewSet(ModelViewSet):
    queryset = AdmissionForm.objects.all()
    serializer_class = AdmissionFormViewSerializer
# =================================================== 
    
    
class FormSubmissionViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = [Isstudent]
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FormSubmissionReadSerializer
        return FormSubmissionSerializer
    
    def perform_create(self, serializer):  
        serializer.save(user=self.request.user)
    
class FormSubmissionReadView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = FormSubmissionReadSerializer
    
    
from .razorpay_client import client
from rest_framework.views import APIView

class RazorpayOrderView(APIView):
    def post(self, request):
        # user = request.user
        amount = int(request.data.get('amount')) * 100
                
        admission_fee = AdmissionFee.objects.create(
            amount=amount / 100,
        )
        
        razor_order = client.order.create({
            "amount":amount,
            "currency":"INR",
            "payment_capture":1
        })
        admission_fee.razorpay_order_id = razor_order["id"]
        admission_fee.save()
        
        return Response({
            "Order_id":razor_order["id"],
            "Key":settings.RAZOR_PAY_KEY_ID,
            "amount":razor_order["amount"]
        })
        

import hmac
import hashlib
from rest_framework import status
from django.conf import settings

import hmac
import hashlib

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class VerifyPaymentView(APIView):
    def post(self, request):
        data = request.data

        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        if not all([order_id, payment_id, signature]):
            return Response({"error": "Missing payment parameters"}, status=status.HTTP_400_BAD_REQUEST)

        secret = settings.RAZOR_PAY_SECRET_KEY

        message = f"{order_id}|{payment_id}"

        generated_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(generated_signature, signature):
            try:
                payment = AdmissionFee.objects.get(razorpay_order_id=order_id)
            except AdmissionFee.DoesNotExist:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.status = "paid"
            payment.save()

            return Response({"status": "success"})

        return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
    

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(APIView):
    def post(self, request):
        payload = request.body
        signature = request.headers.get("X-Razorpay-Signature")

        secret = settings.RAZOR_PAY_SECRET_KEY

        generated_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        if generated_signature == signature:
            data = json.loads(payload)

            if data["event"] == "payment.captured":
                payment_data = data["payload"]["payment"]["entity"]

                order_id = payment_data["order_id"]

                try:
                    payment = AdmissionFee.objects.get(razorpay_order_id=order_id)
                    payment.status = "paid"
                    payment.save()
                except AdmissionFee.DoesNotExist:
                    pass

            return Response({"status": "ok"})

        return Response({"status": "invalid"}, status=400)
    
# NOT IN USE 
class DivisionSetView(ModelViewSet):
    queryset =Student.objects.all()
    serializer_class = DivisionSetSerilaizer

# Only for Post method  
class SetDivisionView(ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = SetDivisionSerializer
    
    def create(self, request, *args, **kwargs):
        division_count = int(request.data.get('division'))
        school_class = request.data.get('SchoolClass')
        capacity = request.data.get('capacity')

        alphabet = list(string.ascii_uppercase[:division_count])

        divisions = []
        for a in alphabet:
            obj = Division.objects.create(
                SchoolClass_id=school_class,  # if FK
                division=a,
                capacity=capacity
            )
            divisions.append(obj)

        serializer = self.get_serializer(divisions, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# This Logic perfom with button after admission and complete and division is set    
@transaction.atomic
def assign_student_divisions():
    # Get all classes
    classes = SchoolClass.objects.all()

    for school_class in classes:
        # Get divisions for this class
        divisions = list(
            Division.objects.filter(school_class=school_class).order_by('id')
        )

        # Skip if no divisions exist
        if not divisions:
            print(f"Skipping {school_class} (no divisions found)")
            continue

        division_len = len(divisions)

        # Get students of this class
        students = list(
            Student.objects.filter(school_class=school_class).order_by('created_at')
        )

        if not students:
            print(f"No students in {school_class}")
            continue

        # Optional: shuffle students for random distribution
        # random.shuffle(students)

        # Assign divisions (round-robin)
        for index, student in enumerate(students):
            student.division = divisions[index % division_len]

        # Bulk update for performance
        Student.objects.bulk_update(students, ['division'])
# ==================================================================

class SetSubjectView(ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SetSubjectSerializer
    

class SyllabusView(ModelViewSet):
    queryset = Syllabus.objects.all()
    serializer_class = SyllabusSerializer


class AssignClassView(ModelViewSet):
    queryset = AssignClass.objects.all()
    serializer_class = AssignClassSerializer
