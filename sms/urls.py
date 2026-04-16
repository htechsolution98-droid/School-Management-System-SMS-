"""
URL configuration for sms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from sms_app.views import *
from django.urls import include
from django.views.generic import TemplateView

from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="Test API documentation",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


router = DefaultRouter()

router.register(r'SchoolView',SchoolView, basename='SchoolView') # DONE
router.register(r'StaffView',StaffView, basename='StaffView') # DONE
router.register(r'studentSignUp',StudentSignUpView, basename='studentSignUp') # On Changing

# both api use togather when student form fill
router.register(r'StudentFIllView', StudentFIllView, basename='StudentFIllView') #  Not in use

# =========ADMISSIONS PROCESS ROUTER========

router.register(r'schoolclass', SchoolClassView, basename='schoolclass')  #only use principle METHOD [GET,POST,PUT,DELETE]
router.register(r'getclass', ClassView, basename='getclass')  #For Admission Form class Drop Down METHOD [GET]

# ===== api for admission  proccess =====
router.register(r'forms', AdmissionFormViewSet, basename='forms')# For Principle use TO create admission form METHOD [POST] 
router.register(r'formstatus', FormStatus, basename='formstatus')# For Principle use TO create admission form METHOD [POST] 

# router.register(r'fields', FormFieldViewSet, basename='fields') #to retrive fields of admission form that added by principle
router.register(r'submissions', FormSubmissionViewSet, basename='submissions')# admission form fill fields METHOD [POST]  ----API Need---  api/schoolclass/ for class drop down
router.register(r'documentsubmission', DocumentSubmissionView, basename='documentsubmission')# admission form fill fields METHOD [POST]  ----API Need---  api/schoolclass/ for class drop down


#===== set only use get this api====== 
router.register(r'StudentDataview', FormSubmissionReadView, basename='StudentDataview') # Not in use



# =====verify api===== after admission sudmission
router.register(r'clerk_doc_fields_check', ClerkVerifyView, basename='ClerkVerifyView') # For solve submission details METHOD [GET,PUT]

router.register(r'PrincipleVerifyView', PrincipleVerifyView, basename='PrincipleVerifyView') # ask
router.register(r'fee_verify', FeeVerifyView, basename='fee_verify')# ask

router.register(r'setSubject', SetSubjectView, basename='setSubject')# For CLerk add subject METHOD [GET,POST,PUT,DELETE]  ----API Need---  api/schoolclass/ for class drop down
router.register(r'divisionSet', SetDivisionView, basename='divisionSet') #For Clerk Use METHOD [GET,POST,PUT,DELETE] ----API Need---  api/schoolclass/ for class drop down

router.register(r'syllabus', SyllabusView, basename='syllabus') # For CLerk add syllabus METHOD [GET,POST,PUT,DELETE]   ----API Need---  api/schoolclass , setSubject for drop down
router.register(r'getteacher', GetTeacherView, basename='getteacher') # For teacher dwop down METHOD [GET]

router.register(r'assignClass', AssignClassView, basename='assignClass')# For CLerk assign Class METHOD [GET,POST,PUT,DELETE] ----API Need---  api/divisionSet/ , api/setSubject/ , api/getteacher/  for drop down

# ========= TIME TABLE ROUTER ============
router.register(r'tt_year', Tt_yearView, basename='tt_year')# For CLerk assign Class METHOD [GET,POST,PUT,DELETE] ----API Need---  api/divisionSet/ , api/setSubject/ , api/getteacher/  for drop down
router.register(r'time_table', Time_tableView, basename='time_table')# For CLerk assign Class METHOD [GET,POST,PUT,DELETE] ----API Need---  api/divisionSet/ , api/setSubject/ , api/getteacher/  for drop down
# router.register(r'tt_day', Tt_dayView, basename='tt_day')# For CLerk assign Class METHOD [GET,POST,PUT,DELETE] ----API Need---  api/divisionSet/ , api/setSubject/ , api/getteacher/  for drop down
router.register(r'tt_daytime', Tt_day_timeView, basename='tt_daytime')# For CLerk assign Class METHOD [GET,POST,PUT,DELETE] ----API Need---  api/divisionSet/ , api/setSubject/ , api/getteacher/  for drop down

router.register(r'get-student',GetStudentView,basename='get-student')# for get student for principle with filter [school filter add remainig]
router.register(r'attendance', AttendanceView, basename='attendance')# For attendance tracking METHOD [GET,POST,PUT,DELETE]
router.register(r'leave-template', LeaveTemplateView, basename='leave-template')# For leave template tracking METHOD [GET,POST,PUT,DELETE]
router.register(r'leave-request', LeaveRequestView, basename='leave-request')# 

router.register(r'get-leave-requests', GetLeaveRequestView, basename='get-leave-requests')# For get leave request for principle with filter [school filter add remainig]
router.register(r'change-leave-status', ChangeLeaveView, basename='change-leave-status')# For approve leave request for principle METHOD [PUT]
router.register(r'announcements', AnnouncementView, basename='announcements')# For managing announcements
router.register(r'get-announcements', GetAnnouncementView, basename='get-announcements')# For get announcement for student,staff with filter [school filter add remainig]   

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include(router.urls)),
    path('api/access/',CustomLoginView.as_view()),  
        
    path('api/refresh/',TokenRefreshView.as_view()),

    path('api/get-location/', GetLocationView.as_view()), #for attendance location
    
    path('api/set-slot/', SetSlotView),
    
    path('api/fields/<str:unique_link>/', FormFieldViewSet.as_view()),
    
     path('api/admission/<str:unique_link>/',Admission),
     path('api/admission/form/link/',ShareFormLink), #to get active form link for admission form fill up
     path('api/checkmobile/',CheckMobileAPIView.as_view()),
     
     # To get remaining leave for staff when click on apply leave button for show remaining leave
     path('api/get-remaining-leaves/',GetRemainingLeaveView.as_view()),
     
    # path('form_page/', TemplateView.as_view(template_name = 'add_form.html')),
    # path('fill_form/',TemplateView.as_view(template_name='form_fill.html')),
    # # path('fillform/<int:id>/submit/',SubmitFormView.as_view()),
    
    # # for admisiion for link
    # path('admission/',TemplateView.as_view(template_name='admisiom_form.html')),
    path('map/',TemplateView.as_view(template_name='map.html')),
    
    path('payment/',TemplateView.as_view(template_name='payment.html')),
    # path('log/',TemplateView.as_view(template_name='login.html')),
    
    # path('in/',TemplateView.as_view(template_name='index.html')),
   
    
    path('api/razor/order/',RazorpayOrderView.as_view()),
    path('api/payment/verify/',VerifyPaymentView.as_view()),
    path('api/offline/payment/',OffilinePaymentView.as_view()),
    path('api/get_receipt/<int:student_id>/<int:form_id>/',get_receipt),
    path('api/webhook/',RazorpayWebhookView.as_view()),
    
     # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),

    # Redoc UI (optional)
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),

    # JSON/YAML schema
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0)),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 
