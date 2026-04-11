from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import random
from django.contrib.auth.models import Group

from django.contrib.auth import get_user_model

User = get_user_model()

def generate_student_username(name):
    Staff_name = name.split(' ')[0]
    digit = string.digits

    four_digit = ''.join(random.choices(digit,k=4))
    Staff_username = Staff_name+four_digit

    if User.objects.filter(username = Staff_username).exists():
        return generate_student_username(name)

    return Staff_username


class CustomeLoginSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        user = self.user
        
        role = user.groups.values_list('name', flat=True)
        data['roles'] =  list(role)
        
        return data
    

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'
        read_only_fields = ['code','login_id']
    

class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['user','school']
        
    def validate_email(self, value):
        if School.objects.filter(email= value).exists():
            raise serializers.ValidationError("Email is already exists.")
        return value

    

class GetTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'
    

class StudentSignUpSerliazer(serializers.ModelSerializer):
    name = serializers.CharField(write_only = True)
    password = serializers.CharField(write_only = True)
    
    class Meta:
        model = User
        fields = ['name','password']
        
    def create(self, validated_data):
        name = validated_data.pop('name')
        password = validated_data.pop('password')
        username = generate_student_username(name)
        
        u = User(username = username)
        u.set_password(password)
        u.save()
        group, created  = Group.objects.get_or_create(name = 'student')
        u.groups.add(group)
        
        return u
# class FieldSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Field
#         fields = ['label', 'field_type']
#         read_only_fields= ['value']


# class FormSerializer(serializers.ModelSerializer):
#     fields = FieldSerializer(many=True)

#     class Meta:
#         model = Form
#         fields = ['id', 'title','email','fields']
       

#     def create(self, validated_data):
#         fields_data = validated_data.pop('fields')

#         form = Form.objects.create(**validated_data)

#         for field in fields_data:
#             Field.objects.create(
#                 form=form,
#                 label=field['label'],
#                 field_type=field['field_type']
#             )

#         return form


# class FromFillSeriliazer(serializers.ModelSerializer):
#     fields = FieldSerializer(many=True,)

#     class Meta:
#         model = Form
#         fields = ['id', 'title', 'fields']





# # use for add set email and add extra fields for student form
# class StudentSerializer(serializers.ModelSerializer):
#     document_fields = serializers.ListField(child=serializers.CharField(),write_only=True)
    
#     class Meta:
#         model = Student
#         fields = ['extra_data','document_fields']
        
#     def create(self, validated_data):
#         # to get document_fields
#         document_fields = validated_data.pop('document_fields', [])

#         student = Student.objects.create(**validated_data)

#         for field in document_fields:
#             StudentDocument.objects.create(student=student, label=field)

#         return student

        
        
# class StudentDocumentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentDocument
#         fields = '__all__'
#         read_only_fields = []
        


class StudentFIllSerilaizer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['email','created_at','is_active','form_filled','principle_verified','fees_verified','clerk_verified','principle_verified_at','clerk_verified_at','fees_verified_at','gr_no']
        





class FeesVerifySerializr(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['first_name',
    'last_name',
    'email',
    'phone',
    'roll_number',
    'course',
    'year',
    'date_of_birth',
    'address',
    'is_active',
    'created_at',
    'extra_data',
    'clerk_verified',
    'clerk_verified_at',
    'principle_verified',
'principle_verified_at'
    
    ]



# =========admissions process serializers========
from rest_framework import serializers
from .models import FormField
import re

import re
from rest_framework import serializers
from .models import SchoolClass


class SchoolClassSerializer(serializers.ModelSerializer):
    school_class = serializers.ListField(
        child=serializers.CharField()
    )

    class Meta:
        model = SchoolClass
        fields = ['school', 'school_class']

    def validate_school_class(self, values):
        validated_classes = []

        basic_classes = ['nursery', 'lkg', 'ukg']
        pattern = r'^(Class\s(1[0-2]|[1-9]))(\s[A-Za-z]+)?$'

        for value in values:
            # Normalize
            value_clean = value.strip()

            # Check Nursery/LKG/UKG
            if value_clean.lower() in basic_classes:
                validated_classes.append(value_clean.title())
                continue

            # Check Class 1–12
            if re.match(pattern, value_clean, re.IGNORECASE):
                validated_classes.append(value_clean.title())
                continue

            raise serializers.ValidationError(
                f"Invalid class format: {value}"
            )

        return validated_classes

    def validate(self, data):
        school = data.get('school')
        class_list = data.get('school_class')

        instance = getattr(self, 'instance', None)

        for school_class in class_list:
            queryset = SchoolClass.objects.filter(
                school=school,
                school_class__iexact=school_class
            )

            if instance:
                queryset = queryset.exclude(id=instance.id)

            if queryset.exists():
                raise serializers.ValidationError(
                    f"{school_class} already exists for this school"
                )

        return data

    def create(self, validated_data):
        school = validated_data.get('school')
        class_list = validated_data.get('school_class')

        objs = [
            SchoolClass(
                school=school,
                school_class=school_class
            )
            for school_class in class_list
        ]

        return SchoolClass.objects.bulk_create(objs)
    
class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'label', 'field_type', 'is_required', 'options', 'order']


class FormSectionSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = FormSection
        fields = ['id', 'title', 'order', 'fields']
        
        

        
# ===========fee structure serializer============
class AdmissionFeeStructureSerializer(serializers.ModelSerializer):
    class_name = serializers.PrimaryKeyRelatedField(
        queryset=SchoolClass.objects.all()
    )
    class Meta:
        model = AdmissionFeeStructure
        fields = ['class_name', 'fee_amount']  
# =================================================



class AdmissionFormSerializer(serializers.ModelSerializer):
    sections = FormSectionSerializer(many=True)
    document_field = serializers.ListField(child=serializers.CharField(),required=False)
    
    fee_structures = AdmissionFeeStructureSerializer(many=True, required=False)
     
    # related_name='fields'
    class Meta:
        model = AdmissionForm
        fields = ['id','fees_enable','fees','title', 'description', 'unique_link','sections','fee_type','fee_structures','document_field']

    def create(self, validated_data):
        document_field = validated_data.pop('document_field',[])
        sections_data = validated_data.pop('sections')
        fee_data = validated_data.pop('fee_structures',[])
        validated_data.pop('school')
        school = self.context['request'].user.school 
        school = self.context['request'].user.school
        if not school:
            raise serializers.ValidationError("User does not have a school assigned")
        
        form = AdmissionForm.objects.create(school = school, **validated_data)

        for section_data in sections_data:
            fields_data = section_data.pop('fields')
            section = FormSection.objects.create(form=form, school = school, **section_data)

            for field_data in fields_data:
                FormField.objects.create(section=section,school = school, **field_data)
                
        
        for label in document_field:
            DocumentField.objects.create(form_id = form,school = school,label=label)
            
        if form.fee_type == 'individual':
            for fee in fee_data:
                AdmissionFeeStructure.objects.create(
                    admission_form=form,
                    **fee
                )

        return form
    

class DocumentFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentField
        fields = ['id','label']
        read_only_fields = ['form_id','school','created_at']
        

# ====this  serializer for view admission form field====

class AdmissionFormViewSerializer(serializers.ModelSerializer):
    sections = FormSectionSerializer(many=True)
    fee_structures = AdmissionFeeStructureSerializer(many=True,read_only=True)
    label = DocumentFieldSerializer(many = True, read_only =True )
    class Meta:
        model = AdmissionForm
        fields = ['id', 'title', 'school','description','sections','fees_enable','fee_type','fees','fee_structures','label']
        
# ===========================================================

class ChangeFormStatus(serializers.ModelSerializer):
    class Meta:
        model = AdmissionForm
        fields = ['is_active']
    
# --------Admission Form submite serializers---------
# 1
class StudentFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFieldValue
        fields = ['field', 'value']   

# 2
from rest_framework.exceptions import ValidationError

class FormSubmissionSerializer(serializers.ModelSerializer):
    field_values = StudentFieldValueSerializer(many=True, write_only=True)

    class Meta:
        model = Student
        fields = ['id', 'form','school', 'school_class', 'mobile', 'field_values']

    def validate(self, data):
        form = data['form']
        field_values = data['field_values']

        # 🔥 get all fields from all sections
        field_map = {
            field.id: field
            for section in form.sections.all()
            for field in section.fields.all()
        }

        for item in field_values:
            field = item.get('field')

            if field.id not in field_map:
                raise serializers.ValidationError(f"Invalid field: {field.id}")

            # ✅ only value validation now
            if field.is_required and not item.get('value'):
                raise serializers.ValidationError(f"{field.label} is required")

        return data
    
    def create(self, validated_data):
        field_values_data = validated_data.pop('field_values')
        
        form = validated_data.pop('form')
        mobile = validated_data.pop('mobile')
        school_class = validated_data.pop('school_class')
        school = validated_data.pop('school')

        if Student.objects.filter(mobile=mobile, details_done=True).exists():
            raise ValidationError({"Error": "This number is not available"})
        
        #  check existing student
        student = Student.objects.filter(
            mobile=mobile,
            details_done=False
        ).first()
        
        
        if student:
            #  UPDATE EXISTING STUDENT
            student.school = school
            student.school_class = school_class
            student.save()

            for item in field_values_data:
                field = item['field']
                value = item.get('value')

                obj, created = StudentFieldValue.objects.update_or_create(
                    student=student,
                    field=field,
                    defaults={
                        'value': value,
                        'form_id': form,
                        'school': school
                    }
                )

            return student

        else:
            #  CREATE NEW STUDENT
            submission = Student.objects.create(
                form=form,
                school=school,
                mobile=mobile,
                school_class=school_class
            )

            values = []
            for item in field_values_data:
                values.append(
                    StudentFieldValue(
                        student=submission,
                        form_id=form,
                        school=school,
                        field=item['field'],
                        value=item.get('value')
                    )
                )

            StudentFieldValue.objects.bulk_create(values)

        return submission
# ============================================================

#------ Admission form document submittion serializers----------
# 1
class DocumentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ['label', 'document']
        
# 2
class DocumentSubmissionSerialiser(serializers.ModelSerializer):
    documents = DocumentItemSerializer(many=True, write_only=True)

    class Meta:
        model = DocumentFile
        fields = ['form_id', 'school', 'student', 'documents']

    from rest_framework.exceptions import ValidationError

    def create(self, validated_data):
        documents_data = validated_data.pop('documents')
        
        student = validated_data.get('student')
        form = validated_data.get('form_id')
        school = validated_data.get('school')

        # ❌ CASE 1: Documents already completed
        if student.details_done:
            raise ValidationError({
                "student": "Documents process already completed"
            })

        instances = []

        for doc in documents_data:
            label = doc.get('label')
            document = doc.get('document')

            # 🔄 CASE 2: Update if already exists
            obj, created = DocumentFile.objects.update_or_create(
                student=student,
                label=label,   # 👈 important: unique per label
                defaults={
                    'form_id': form,
                    'school': school,
                    'document': document
                }
            )

            instances.append(obj)

        return instances
# =======================================================================

class MobileCheckSerializer(serializers.Serializer):
    mobile = serializers.CharField()
# For viewing data 

class StudentFieldValueReadSerializer(serializers.ModelSerializer):
    field_label = serializers.CharField(source='field.label')

    class Meta:
        model = StudentFieldValue
        fields = ['field_label', 'value', 'file']


class FormSubmissionReadSerializer(serializers.ModelSerializer):
    field_values = StudentFieldValueReadSerializer(many=True)

    class Meta:
        model = Student
        fields = ['id', 'created_at', 'field_values']
        
# Only for Post method    
class SetDivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ['SchoolClass','division','capacity']
        

# =========serializers for set division by clerk========
# NOT IN USE
import string
class DivisionSetSerilaizer(serializers.ModelSerializer):
    capacity =  serializers.IntegerField(write_only = True)
    class Meta:
        model = Student
        fields = ['division','capacity'] 
    
    def create(self, validated_data):
        total_division = int(validated_data.pop('division'))
        capacity = validated_data.pop('capacity')
        
        alphabet = string.ascii_uppercase[:total_division]
        
        alphabet_len = len(alphabet)
        
        alphabet = list(string.ascii_uppercase[:alphabet_len])

        students = Student.objects.all().order_by('created_at')

        for index, student in enumerate(students):
            division = alphabet[index % alphabet_len]  # round-robin assignment
            student.division = division
            student.save()
        
        return students
        

# clerk side verify serializer

class DocumentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ['id', 'label', 'document']
        
class ClerkVerifySerializr(serializers.ModelSerializer):
    field_values = StudentFieldValueReadSerializer(many=True, read_only=True)
    documents = DocumentReadSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = [
            'is_active',
            'details_done',
            'principle_verified',
            'principle_verified_at',
            'fees_verified',
            'fees_verified_at',
            'school',
            'gr_no',
            'user'
        ]



class PrincipleVerifySerializr(serializers.ModelSerializer):
    field_values = StudentFieldValueReadSerializer(many=True,read_only=True)
    class Meta:
        model = Student
        fields = ['principle_verified','principle_verified_at','field_values']
       

# =======set subject serializers========

class SetSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ['school']
        
class SyllabusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Syllabus
        fields = '__all__'
        read_only_fields = ['school']


class AssignClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignClass
        fields = '__all__'


# class Tt_daySerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = Tt_day
#         fields  = ['year','day','lecture','school_class']
#         read_only_fields = ['year']


class Tt_day_timeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tt_day_time
        fields= '__all__'
        read_only_fields = ['day']
        
class Tt_breaksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tt_breaks
        fields = '__all__'
        read_only_fields = ['day']


from django.db import transaction

class Tt_yearSerializer(serializers.ModelSerializer):
    start_year = serializers.IntegerField(write_only=True)
    end_year = serializers.IntegerField(write_only=True)

    day = serializers.CharField(write_only=True)
    lecture = serializers.CharField(write_only=True)
    school_class = serializers.PrimaryKeyRelatedField(
        queryset=Division.objects.all(),
        write_only=True
    )    
    day_time = Tt_day_timeSerializer(write_only=True)
    breaks = Tt_breaksSerializer(write_only=True, many=True)

    class Meta:
        model = Tt_year
        fields = ['id', 'year', 'start_year', 'end_year', 'day', 'lecture','school_class','day_time', 'breaks']
        read_only_fields = ['year']

    def validate(self, data):
        start = data.get('start_year')
        end = data.get('end_year')

        if len(str(start)) != 4 or len(str(end)) != 4:
            raise serializers.ValidationError("Year must be 4 digits")

        if not (1900 <= start <= 2100):
            raise serializers.ValidationError("Start year must be between 1900 and 2100")

        if not (1900 <= end <= 2100):
            raise serializers.ValidationError("End year must be between 1900 and 2100")

        if end != start + 1:
            raise serializers.ValidationError("End year must be start_year + 1")

        return data

    def create(self, validated_data):
        start = validated_data.pop('start_year')
        end = validated_data.pop('end_year')
        
        day = validated_data.pop('day')
        lecture = validated_data.pop('lecture')
        school_class = validated_data.pop('school_class')
        
        day_time_data = validated_data.pop('day_time')
        
        breaks_data = validated_data.pop('breaks')

        year_str = f"{start}-{str(end)[-2:]}"

        if Tt_year.objects.filter(year=year_str).exists():
            raise serializers.ValidationError("This academic year already exists")

        with transaction.atomic():
            tt_year = Tt_year.objects.create(year=year_str)

            tt_day = Tt_day.objects.create(
                year=tt_year,
                day=day,
                school_class = school_class,
                lecture=lecture
            )

            Tt_day_time.objects.create(
                day=tt_day,
                start=day_time_data.get('start'),
                end=day_time_data.get('end')
            )

            for b in breaks_data:
                Tt_breaks.objects.create(
                    day=tt_day,
                    total_breaks=b.get('total_breaks'),
                    breaks=b.get('breaks'),
                    time=b.get('time'),
                    description=b.get('description')
                )

        return tt_year  # ✅ FIX: return main object

    def to_representation(self, instance):
        days = instance.tt_day_set.all()

        return {
            "id": instance.id,
            "year": instance.year,
            "days": [
                {
                    "day": d.day,
                    "lecture": d.lecture
                } for d in days
            ]
        }