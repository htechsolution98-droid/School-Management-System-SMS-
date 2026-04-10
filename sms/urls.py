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


#===== set only use get this api====== 
router.register(r'StudentDataview', FormSubmissionReadView, basename='StudentDataview') # Not in use



# =====verify api===== after admission sudmission
router.register(r'ClerkVerify', ClerkVerifyView, basename='ClerkVerifyView') # For solve submission details METHOD [GET,PUT]
router.register(r'PrincipleVerifyView', PrincipleVerifyView, basename='PrincipleVerifyView') # ask
router.register(r'FeeVerifyView', FeeVerifyView, basename='FeeVerifyView')# ask

router.register(r'setSubject', SetSubjectView, basename='setSubject')# For CLerk add subject METHOD [GET,POST,PUT,DELETE]  ----API Need---  api/schoolclass/ for class drop down
router.register(r'divisionSet', SetDivisionView, basename='divisionSet') #For Clerk Use METHOD [GET,POST,PUT,DELETE] ----API Need---  api/schoolclass/ for class drop down

router.register(r'syllabus', SyllabusView, basename='syllabus') # For CLerk add syllabus METHOD [GET,POST,PUT,DELETE]   ----API Need---  api/schoolclass , setSubject for drop down
router.register(r'getteacher', GetTeacherView, basename='getteacher') # For teacher dwop down METHOD [GET]

router.register(r'assignClass', AssignClassView, basename='assignClass')# For CLerk assign Class METHOD [GET,POST,PUT,DELETE] ----API Need---  api/divisionSet/ , api/setSubject/ , api/getteacher/  for drop down


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include(router.urls)),
    path('api/access/',CustomLoginView.as_view()),  
        
    path('api/refresh/',TokenRefreshView.as_view()),
    
    path('api/fields/<str:unique_link>/', FormFieldViewSet.as_view()),
    
     path('admission/<str:unique_link>/',Admission),
     path('admission/form/link/',ShareFormLink),
     
    # path('form_page/', TemplateView.as_view(template_name = 'add_form.html')),
    # path('fill_form/',TemplateView.as_view(template_name='form_fill.html')),
    # # path('fillform/<int:id>/submit/',SubmitFormView.as_view()),
    
    # # for admisiion for link
    # path('admission/',TemplateView.as_view(template_name='admisiom_form.html')),
    
    # path('payment/',TemplateView.as_view(template_name='payment.html')),
    # path('log/',TemplateView.as_view(template_name='login.html')),
    
    # path('in/',TemplateView.as_view(template_name='index.html')),
   
    
    path('razor/order/',RazorpayOrderView.as_view()),
    path('payment/verify/',VerifyPaymentView.as_view()),
    path('webhook/',RazorpayWebhookView.as_view()),
    
     # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),

    # Redoc UI (optional)
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),

    # JSON/YAML schema
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0)),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 