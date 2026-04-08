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



class SchoolClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchoolClass
        fields = ['school_class']
    
    def validate_school_class(self, value):
        """
        Validates that the input is either:
        - Nursery, LKG, UKG
        - Class 1, Class 2, ... Class 12, optionally followed by a stream (e.g., Science, Commerce, Arts)
        """
        # Accept nursery/lkg/ukg (case-insensitive)
        basic_classes = ['nursery', 'lkg', 'ukg']
        if value.lower() in basic_classes:
            return value.title()

        # Accept class 1-12 optionally with stream
        pattern = r'^(Class\s(1[0-2]|[1-9]))(\s[A-Za-z]+)?$'
        if re.match(pattern, value, re.IGNORECASE):
            return value.title()
        
        raise serializers.ValidationError(
            "Invalid format. Examples: 'Nursery', 'Class 11 Science', 'Class 5'."
        )
    
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
    fee_structures = AdmissionFeeStructureSerializer(many=True, required=False)
     
    related_name='fields'
    class Meta:
        model = AdmissionForm
        fields = ['id','fees_enable','fees','title', 'description', 'unique_link','sections','fee_type','fee_structures']

    def create(self, validated_data):
        sections_data = validated_data.pop('sections')
        fee_data = validated_data.pop('fee_structures',[])
        form = AdmissionForm.objects.create(**validated_data)

        for section_data in sections_data:
            fields_data = section_data.pop('fields')
            section = FormSection.objects.create(form=form, **section_data)

            for field_data in fields_data:
                FormField.objects.create(section=section, **field_data)
                
                
        if form.fee_type == 'individual':
            for fee in fee_data:
                AdmissionFeeStructure.objects.create(
                    admission_form=form,
                    **fee
                )

        return form
    



# ====this  serializer for view admission form field====

class AdmissionFormViewSerializer(serializers.ModelSerializer):
    sections = FormSectionSerializer(many=True)
    fee_structures = AdmissionFeeStructureSerializer(many=True,read_only=True)

    class Meta:
        model = AdmissionForm
        fields = ['id', 'title', 'description','sections','fees_enable','fee_type','fees','fee_structures']
        
# ===========================================================      

class StudentFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFieldValue
        fields = ['field', 'value', 'file']

class FormSubmissionSerializer(serializers.ModelSerializer):
    field_values = StudentFieldValueSerializer(many=True, write_only=True)

    class Meta:
        model = Student
        fields = ['id', 'form','school_class','field_values']

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

            if field.is_required:
                if field.field_type == 'file' and not item.get('file'):
                    raise serializers.ValidationError(f"{field.label} is required")
                elif field.field_type != 'file' and not item.get('value'):
                    raise serializers.ValidationError(f"{field.label} is required")

        return data

    def create(self, validated_data):
        field_values_data = validated_data.pop('field_values')

        submission = Student.objects.create(**validated_data)

        values = []
        for item in field_values_data:
            values.append(
                StudentFieldValue(
                    student=submission,
                    field=item['field'],
                    value=item.get('value'),
                    file=item.get('file')
                )
            )

        StudentFieldValue.objects.bulk_create(values)

        return submission
    
    
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

class ClerkVerifySerializr(serializers.ModelSerializer):
    field_values = StudentFieldValueReadSerializer(many=True,read_only=True)

    class Meta:
        model = Student
        fields = '__all__'



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
        
class SyllabusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Syllabus
        fields = '__all__'


class AssignClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignClass
        fields = '__all__'