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
from rest_framework.decorators import api_view
from django.db.models import Q

from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your views here.
# set access and refresh token in cookie 
class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomeLoginSerializer

    # def post(self, request, *args, **kwargs):
    #     response = super().post(request, *args, **kwargs)

    #     if response.status_code == 200:
    #         access = response.data.pop('access', None)
    #         refresh = response.data.pop('refresh', None)

    #         response.set_cookie(
    #             key='access_token',
    #             value=access,
    #             httponly=True,
    #             secure=False,  # True in production (HTTPS)
    #             samesite='Lax'
    #         )

    #         response.set_cookie(
    #             key='refresh_token',
    #             value=refresh,
    #             httponly=True,
    #             secure=False,
    #             samesite='Lax'
    #         )

    #     return response
    

from rest_framework_simplejwt.views  import TokenRefreshView

# class CookieTokenRefreshView(TokenRefreshView):
#     def post(self, request, *args, **kwargs):
        
#         refresh_token = request.COOKIES.get('refresh_token')
        
#         if not refresh_token:
#             return None
        
#         request.data['refresh'] = refresh_token
        
#         response = super().post(request, *args, **kwargs)
        
#         if response.status_code == 200:
#             access_token = response.get('access')
            
#             response.set_cookie(
#                 key='access_token',
#                 value=access_token,
#                 httponly=True,
#                 secure=False,
#                 samesite='Lax'
#             )
            
#         return response
            
            
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
    permission_classes = [IsAuthenticated]

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

            school = serializer.save(code=school_code, login_id=user)
            user.school = school
            user.save()

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
        user.school = self.request.user.school
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


class GetTeacherView(ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = GetTeacherSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return Staff.objects.filter(user__groups__name = "TEACHER")
    
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
# this for only get its public use on Admission fprosecc
class ClassView(ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    http_method_names = ['get']
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import SchoolClass
# from .serializers import SchoolClassSerializer


class SchoolClassView(ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # ✅ only show classes of logged-in user's school
        return SchoolClass.objects.filter(school=self.request.user.school)

    def create(self, request, *args, **kwargs):
        # ✅ accept multiple objects   
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        # save with school
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
#     def list(self, request, *args, **kwargs):
#         school_id = request.user.school.id
#         cache_key = f"school_classes_{school_id}"

#         data = cache.get(cache_key)
        
#         if data:
#             print("cach")

#         if not data:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#             data = serializer.data

#             cache.set(cache_key, data, timeout=60*10)

#         return Response(data)

#     def perform_create(self, serializer):
#         serializer.save(school=self.request.user.school)

#         instance = serializer.save()
#         cache.delete(f"school_classes_{instance.school.id}")

#     def perform_update(self, serializer):
#         instance = serializer.save()
#         cache.delete(f"school_classes_{instance.school.id}")

#     def perform_destroy(self, instance):
#         school_id = instance.school.id
#         instance.delete()
#         cache.delete(f"school_classes_{school_id}")
        
#     def create(self, request, *args, **kwargs):
#         super().create(request, *args, **kwargs)
#         return Response({
#             "message": "Class created Successfully"
#         }, status=201)
# # ========================================
    
# ========= admissions process views ========
from rest_framework import status

# ========= using this serializers principle set DocumentField=========

# class DocumentFieldview(ModelViewSet):
#     queryset = DocumentField.objects.all()
#     serializer_class = DocumentFileSerializer
    
# =====================================================================


class AdmissionFormViewSet(ModelViewSet):
    queryset = AdmissionForm.objects.all()
    serializer_class = AdmissionFormSerializer
    permission_classes = [IsAuthenticated]
    
    lookup_field = 'unique_link' 
    # access form via UUID

    def get_queryset(self):
        return AdmissionForm.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
        print(self.request.user)
     
    # def create(self, request, *args, **kwargs):
    #     serializer = super().create(request, *args, **kwargs)
        
    #     return Response({
    #         "meassage":"Form created Successfully"
    #         }, status=status.HTTP_201_CREATED)
   
   
# ====this view set for view admission form field====

class FormFieldViewSet(RetrieveAPIView):
    queryset = AdmissionForm.objects.all()
    serializer_class = AdmissionFormViewSerializer
    lookup_field = 'unique_link'
    
    def get_queryset(self):
        return AdmissionForm.objects.filter(is_active=True)

# ===================================================
# for admission form status change /
class FormStatus(ModelViewSet):
    queryset = AdmissionForm.objects.all()
    serializer_class = ChangeFormStatus
    serializer_class = [IsAuthenticated,Isprincipal]
    http_method_names = ['patch']

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        is_active = request.data.get('is_active')

        with transaction.atomic():
            # If setting this form to active
            if is_active is True or is_active == 'true':
                # Make all other forms inactive
                AdmissionForm.objects.exclude(id=instance.id).update(is_active=False)

            # Update current instance
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({
            "message": "Form Public successfully",
            # "data": serializer.data
        }, status=status.HTTP_200_OK)

# for send form link
@api_view(['GET'])
def ShareFormLink(request):
    form = AdmissionForm.objects.filter(is_active = True).first()
    
    form_link = f"http://127.0.0.1:8000/admission/{form.unique_link}/"
    
    return Response({
         "form_link":form_link
    })
    
# this for craete admission link
def Admission(request, unique_link):
    form = AdmissionForm.objects.filter(unique_link = unique_link).first()
    
    if not form:
        school = School.objects.filter(login_id = form.school )
        return render(request, "error.html", {"mobile": school.email ,"email":school.phone})
    
    # if not form.is_active:
    #     return render(request, "error.html", {"message": "Form Is Not Active"})
        
    return render(request, "index.html",{'unique_link':unique_link})

    
class FormSubmissionViewSet(ModelViewSet):
    queryset = Student.objects.all()
    # serializer_class = [Isstudent]
    serializer_class = FormSubmissionSerializer
    
    # def get_serializer_class(self):
    #     if self.action in ['list', 'retrieve']:
    #         return FormSubmissionReadSerializer
    #     return FormSubmissionSerializer
    
    # def perform_create(self, serializer):  
    #     serializer.save(user=self.request.user)


    
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import DocumentFile

from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import DocumentFile
# from .serializers import DocumentSubmissionSerialiser


class DocumentSubmissionView(ModelViewSet):
    queryset = DocumentFile.objects.all()
    serializer_class = DocumentSubmissionSerialiser
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        data = request.data  # ✅ NO .copy()

        documents = []
        i = 0

        while True:
            label = data.get(f'documents[{i}][label]')
            document = data.get(f'documents[{i}][document]')

            if not label and not document:
                break

            documents.append({
                "label": label,
                "document": document
            })
            i += 1

        # ✅ Build new clean dict (important)
        final_data = {
            "form_id": data.get("form_id"),
            "school": data.get("school"),
            "student": data.get("student"),
            "documents": documents
        }

        serializer = self.get_serializer(data=final_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "message": "Documents uploaded successfully"
        })
class FormSubmissionReadView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = FormSubmissionReadSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CheckMobileAPIView(APIView):
    def post(self, request):
        serializer = MobileCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']

        student = Student.objects.filter(mobile=mobile).first()

        # ❌ CASE 1: Already used
        if student and student.details_done:
            return Response({
                "status": "used",
                "message": "This number is already used"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 🔄 CASE 2: Resume
        if student and not student.details_done:
            values = StudentFieldValue.objects.filter(student=student)

            return Response({
                # "status": "resume",
                "id": student.id,
                "mobile": student.mobile,
                "school": student.school.id if student.school else None,
                "school_class": student.school_class.id if student.school_class else None,
                "field_values": [
                    {
                        "field": v.field.id,
                        "value": v.value
                    }
                    for v in values
                ]
            }, status=status.HTTP_200_OK)

        # 🆕 CASE 3: New number
        return Response({
            "status": "new",
            "message": "Mobile number is available"
        }, status=status.HTTP_200_OK)    
    
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

# Only for Post method  from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django.core.cache import cache
import string


class SetDivisionView(ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = SetDivisionSerializer
    # permission_classes = [IsAuthenticated, IsCLerk]

    # ✅ GET (LIST with Redis Cache)
    def list(self, request, *args, **kwargs):
        school_id = request.user.school.id

        cache_key = f"divisions_school_{school_id}"

        # ✅ Check Cache
        cached_data = cache.get(cache_key)
        # if cached_data:
        #     return Response({
        #         "message": "Data fetched from cache",
        #         "data": cached_data
        #     })

        # ✅ Fetch from DB
        queryset = Division.objects.filter(school_id=school_id)
        serializer = self.get_serializer(queryset, many=True)

        # ✅ Store in Redis
        cache.set(cache_key, serializer.data, timeout=60 * 10)

        return Response(serializer.data)

    # ✅ CREATE (already done, just kept here)
    def create(self, request, *args, **kwargs):
        division_count = request.data.get('division')
        school_class = request.data.get('SchoolClass')
        capacity = request.data.get('capacity')

        if not division_count:
            return Response({"error": "division is required"}, status=400)

        if not school_class:
            return Response({"error": "SchoolClass is required"}, status=400)

        if not capacity:
            return Response({"error": "capacity is required"}, status=400)

        try:
            division_count = int(division_count)
            capacity = int(capacity)
        except ValueError:
            return Response({"error": "division and capacity must be integers"}, status=400)

        if division_count <= 0 or division_count > 26:
            return Response({"error": "division must be between 1 and 26"}, status=400)

        existing = Division.objects.filter(SchoolClass_id=school_class).count()
        if existing > 0:
            return Response(
                {"error": "Divisions already exist for this class"},
                status=400
            )

        alphabet = list(string.ascii_uppercase[:division_count])

        divisions = []
        for a in alphabet:
            obj = Division.objects.create(
                SchoolClass_id=school_class,
                division=a,
                school=self.request.user.school,
                capacity=capacity,
            )
            divisions.append(obj)

        # ✅ Clear Cache
        cache.delete(f"divisions_{school_class}")

        serializer = self.get_serializer(divisions, many=True)

        return Response({
            "message": "Division created Successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


    # ✅ UPDATE (clear cache)
    def perform_update(self, serializer):
        instance = serializer.save()

        cache_key = f"divisions_{instance.SchoolClass_id}"
        cache.delete(cache_key)


    # ✅ DELETE (clear cache)
    def perform_destroy(self, instance):
        cache_key = f"divisions_{instance.SchoolClass_id}"
        cache.delete(cache_key)

        instance.delete()
    
    

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

from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

class SetSubjectView(ModelViewSet):
    serializer_class = SetSubjectSerializer
    permission_classes = [IsAuthenticated, IsCLerk]

    # ✅ Restrict queryset to user's school (IMPORTANT)
    def get_queryset(self):
        return Subject.objects.filter(school=self.request.user.school)

    # ✅ CREATE
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save(school=request.user.school)

        # ✅ Clear cache
        school_id = request.user.school.id
        school_class = instance.id

        cache.delete(f"subjects_{school_id}_all")
        cache.delete(f"subjects_{school_id}_{school_class}")

        return Response({
            "message": "Subject created successfully",
            # "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    # ✅ LIST (GET ALL WITH CACHE)
    def list(self, request, *args, **kwargs):
        school_id = request.user.school.id
        school_class = request.query_params.get("SchoolClass")

        cache_key = f"subjects_{school_id}_{school_class if school_class else 'all'}"

        # ✅ Check cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({
                "message": "Data fetched from cache",
                "data": cached_data
            })

        queryset = self.get_queryset()

        if school_class:
            queryset = queryset.filter(SchoolClass_id=school_class)

        serializer = self.get_serializer(queryset, many=True)

        # ✅ Set cache
        cache.set(cache_key, serializer.data, timeout=60 * 10)

        return Response({
            "message": "Data fetched from DB",
            "data": serializer.data
        })

    # ✅ RETRIEVE
    def retrieve(self, request, *args, **kwargs):
        subject_id = kwargs.get("pk")
        cache_key = f"subject_{subject_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({
                "message": "Data fetched from cache",
                "data": cached_data
            })

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        cache.set(cache_key, serializer.data, timeout=60 * 10)

        return Response({
            "message": "Data fetched from DB",
            "data": serializer.data
        })

    # ✅ UPDATE
    def perform_update(self, serializer):
        instance = serializer.save()

        school_id = instance.school.id
        school_class = instance.SchoolClass_id

        cache.delete(f"subjects_{school_id}_all")
        cache.delete(f"subjects_{school_id}_{school_class}")
        cache.delete(f"subject_{instance.id}")

    # ✅ DELETE
    def perform_destroy(self, instance):
        school_id = instance.school.id
        school_class = instance.SchoolClass_id

        cache.delete(f"subjects_{school_id}_all")
        cache.delete(f"subjects_{school_id}_{school_class}")
        cache.delete(f"subject_{instance.id}")

        instance.delete()
    

from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

class SyllabusView(ModelViewSet):
    serializer_class = SyllabusSerializer

    # ✅ Restrict to user's school
    def get_queryset(self):
        return Syllabus.objects.filter(school=self.request.user.school)

    # ✅ CREATE
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save(school=request.user.school)

        school_id = request.user.school.id
        school_class = instance.SchoolClass_id

        # ✅ Clear cache
        cache.delete(f"syllabus_{school_id}_all")
        cache.delete(f"syllabus_{school_id}_{school_class}")

        return Response({
            "message": "Syllabus created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    # ✅ LIST (WITH CACHE)
    def list(self, request, *args, **kwargs):
        school_id = request.user.school.id
        school_class = request.query_params.get("SchoolClass")

        cache_key = f"syllabus_{school_id}_{school_class if school_class else 'all'}"

        # ✅ Check cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({
                "message": "Data fetched from cache",
                "data": cached_data
            })

        queryset = self.get_queryset()

        if school_class:
            queryset = queryset.filter(SchoolClass_id=school_class)

        serializer = self.get_serializer(queryset, many=True)

        # ✅ Store cache
        cache.set(cache_key, serializer.data, timeout=60 * 10)

        return Response({
            "message": "Data fetched from DB",
            "data": serializer.data
        })

    # ✅ RETRIEVE
    def retrieve(self, request, *args, **kwargs):
        syllabus_id = kwargs.get("pk")
        cache_key = f"syllabus_single_{syllabus_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({
                "message": "Data fetched from cache",
                # "data": cached_data
            })

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        cache.set(cache_key, serializer.data, timeout=60 * 10)

        return Response({
            "message": "Data fetched from DB",
            "data": serializer.data
        })

    # ✅ UPDATE
    def perform_update(self, serializer):
        instance = serializer.save()

        school_id = instance.school.id
        school_class = instance.id

        cache.delete(f"syllabus_{school_id}_all")
        cache.delete(f"syllabus_{school_id}_{school_class}")
        cache.delete(f"syllabus_single_{instance.id}")

    # ✅ DELETE
    def perform_destroy(self, instance):
        school_id = instance.school.id
        school_class = instance.id

        cache.delete(f"syllabus_{school_id}_all")
        cache.delete(f"syllabus_{school_id}_{school_class}")
        cache.delete(f"syllabus_single_{instance.id}")

        instance.delete()


class AssignClassView(ModelViewSet):
    queryset = AssignClass.objects.all()
    serializer_class = AssignClassSerializer

# ========= TIME TABLE VIEWs============

class Tt_yearView(ModelViewSet):
    queryset = Tt_year.objects.all()
    serializer_class = Tt_yearSerializer
    
# class Tt_dayView(ModelViewSet): 
#     queryset = Tt_day.objects.all()
#     serializer_class = Tt_daySerializer
    
class Tt_day_timeView(ModelViewSet):  
    queryset = Tt_day_time.objects.all()
    serializer_class = Tt_day_timeSerializer 