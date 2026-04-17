from datetime import timedelta
from xml.parsers.expat import model

from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import random
from django.contrib.auth.models import Group

from django.contrib.auth import get_user_model

User = get_user_model()


def generate_student_username(name):
    Staff_name = name.split(" ")[0]
    digit = string.digits

    four_digit = "".join(random.choices(digit, k=4))
    Staff_username = Staff_name + four_digit

    if User.objects.filter(username=Staff_username).exists():
        return generate_student_username(name)

    return Staff_username


class CustomeLoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        role = user.groups.values_list("name", flat=True)
        data["roles"] = list(role)

        return data


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"
        read_only_fields = ["code", "login_id"]


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = "__all__"
        read_only_fields = ["user", "school"]

    def validate_email(self, value):
        if School.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already exists.")
        return value


class GetTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'name']


class StudentSignUpSerliazer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["name", "password"]

    def create(self, validated_data):
        name = validated_data.pop("name")
        password = validated_data.pop("password")
        username = generate_student_username(name)

        u = User(username=username)
        u.set_password(password)
        u.save()
        group, created = Group.objects.get_or_create(name="student")
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
        fields = "__all__"
        read_only_fields = [
            "email",
            "created_at",
            "is_active",
            "form_filled",
            "principle_verified",
            "fees_verified",
            "clerk_verified",
            "principle_verified_at",
            "clerk_verified_at",
            "fees_verified_at",
            "gr_no",
        ]


class StudentFieldValueReadSerializerForFee(serializers.ModelSerializer):
    field_label = serializers.CharField(source="field.label", read_only=True)

    class Meta:
        model = StudentFieldValue
        fields = ["id", "field", "field_label", "value"]


class FeeDatailesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionFee
        fields = ["amount", "currency", "payment_mode", "fee_verify", "paid_at"]
        read_only_fields = ["amount", "currency", "payment_mode"]


from django.utils import timezone


# -------------------------------
class FeesVerifySerializr(serializers.ModelSerializer):
    fee = serializers.SerializerMethodField()
    field_values = StudentFieldValueReadSerializerForFee(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "mobile",
            "fees_verified",
            "fees_verified_at",
            "fee",
            "field_values",
        ]
        read_only_fields = ["id", "user", "mobile", "field_values"]

    # ✅ Get latest fee
    def get_fee(self, obj):
        fee = obj.fee.order_by("-created_at").first()
        return FeeDatailesSerializer(fee).data if fee else None

    # ✅ Update both Student + AdmissionFee
    def update(self, instance, validated_data):
        request = self.context.get("request")

        # -------------------------------
        # Update Student fields
        # -------------------------------
        instance.fees_verified = validated_data.get(
            "fees_verified", instance.fees_verified
        )

        instance.fees_verified_at = validated_data.get(
            "fees_verified_at", timezone.now()
        )

        instance.save()

        # -------------------------------
        # Update AdmissionFee fields
        # -------------------------------
        fee = instance.fee.order_by("-created_at").first()

        if fee:
            fee.fee_verify = request.data.get("fee_verify", fee.fee_verify)

            fee.fee_verify = True
            fee.paid_at = timezone.now()

            fee.save()

        return instance


# =========admissions process serializers========
from rest_framework import serializers
from .models import FormField
import re

import re
from rest_framework import serializers
from .models import SchoolClass

import re
from rest_framework import serializers
from .models import SchoolClass

import re
from rest_framework import serializers
from .models import SchoolClass


class SchoolClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchoolClass
        fields = ["id", "school_class"]

    def validate(self, data):
        request = self.context.get("request")
        school = request.user.school
        school_class = data.get("school_class")

        # Prevent duplicate in DB
        if SchoolClass.objects.filter(
            school=school, school_class__iexact=school_class
        ).exists():
            raise serializers.ValidationError(f"{school_class} already exists")

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        school = request.user.school

        return SchoolClass.objects.create(
            school=school, school_class=validated_data["school_class"]
        )


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ["id", "label", "field_type", "is_required", "options", "order"]


class FormSectionSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = FormSection
        fields = ["id", "title", "order", "fields"]


# ===========fee structure serializer============
class AdmissionFeeStructureSerializer(serializers.ModelSerializer):
    class_name = serializers.PrimaryKeyRelatedField(queryset=SchoolClass.objects.all())

    class Meta:
        model = AdmissionFeeStructure
        fields = ["class_name", "fee_amount"]


# =================================================


class AdmissionFormSerializer(serializers.ModelSerializer):
    sections = FormSectionSerializer(many=True)
    document_field = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    fee_structures = AdmissionFeeStructureSerializer(many=True, required=False)

    # related_name='fields'
    class Meta:
        model = AdmissionForm
        fields = [
            "id",
            "is_active",
            "fees_enable",
            "fees",
            "title",
            "description",
            "unique_link",
            "sections",
            "fee_type",
            "fee_structures",
            "document_field",
        ]

    def create(self, validated_data):
        document_field = validated_data.pop("document_field", [])
        sections_data = validated_data.pop("sections")
        fee_data = validated_data.pop("fee_structures", [])
        validated_data.pop("school")
        school = self.context["request"].user.school
        school = self.context["request"].user.school
        if not school:
            raise serializers.ValidationError("User does not have a school assigned")

        form = AdmissionForm.objects.create(school=school, **validated_data)

        for section_data in sections_data:
            fields_data = section_data.pop("fields")
            section = FormSection.objects.create(
                form=form, school=school, **section_data
            )

            for field_data in fields_data:
                FormField.objects.create(section=section, school=school, **field_data)

        for label in document_field:
            DocumentField.objects.create(form_id=form, school=school, label=label)

        if form.fee_type == "individual":
            for fee in fee_data:
                AdmissionFeeStructure.objects.create(admission_form=form, **fee)

        return form


class DocumentFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentField
        fields = ["id", "label"]
        read_only_fields = ["form_id", "school", "created_at"]


# ====this  serializer for view admission form field====


class AdmissionFormViewSerializer(serializers.ModelSerializer):
    sections = FormSectionSerializer(many=True)
    fee_structures = AdmissionFeeStructureSerializer(many=True, read_only=True)
    label = DocumentFieldSerializer(many=True, read_only=True)

    class Meta:
        model = AdmissionForm
        fields = [
            "id",
            "title",
            "school",
            "description",
            "sections",
            "fees_enable",
            "fee_type",
            "fees",
            "fee_structures",
            "label",
        ]


# ===========================================================


class ChangeFormStatus(serializers.ModelSerializer):
    class Meta:
        model = AdmissionForm
        fields = ["is_active"]


# --------Admission Form submite serializers---------
# 1
class StudentFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFieldValue
        fields = ["field", "value"]


# 2
from rest_framework.exceptions import ValidationError


class FormSubmissionSerializer(serializers.ModelSerializer):
    field_values = StudentFieldValueSerializer(many=True, write_only=True)

    class Meta:
        model = Student
        fields = ["id", "form", "school", "school_class", "mobile", "field_values"]

    def validate(self, data):
        form = data["form"]
        field_values = data["field_values"]

        # 🔥 get all fields from all sections
        field_map = {
            field.id: field
            for section in form.sections.all()
            for field in section.fields.all()
        }

        for item in field_values:
            field = item.get("field")

            if field.id not in field_map:
                raise serializers.ValidationError(f"Invalid field: {field.id}")

            # ✅ only value validation now
            if field.is_required and not item.get("value"):
                raise serializers.ValidationError(f"{field.label} is required")

        return data

    def create(self, validated_data):
        field_values_data = validated_data.pop("field_values")

        form = validated_data.pop("form")
        mobile = validated_data.pop("mobile")
        school_class = validated_data.pop("school_class")
        school = validated_data.pop("school")

        if Student.objects.filter(mobile=mobile, details_done=True).exists():
            raise ValidationError({"Error": "This number is not available"})

        #  check existing student
        student = Student.objects.filter(mobile=mobile, details_done=False).first()

        if student:
            #  UPDATE EXISTING STUDENT
            student.school = school
            student.school_class = school_class
            student.save()

            for item in field_values_data:
                field = item["field"]
                value = item.get("value")

                obj, created = StudentFieldValue.objects.update_or_create(
                    student=student,
                    field=field,
                    defaults={"value": value, "form_id": form, "school": school},
                )

            return student

        else:
            #  CREATE NEW STUDENT
            submission = Student.objects.create(
                form=form, school=school, mobile=mobile, school_class=school_class
            )

            values = []
            for item in field_values_data:
                values.append(
                    StudentFieldValue(
                        student=submission,
                        form_id=form,
                        school=school,
                        field=item["field"],
                        value=item.get("value"),
                    )
                )

            StudentFieldValue.objects.bulk_create(values)

        return submission


# ============================================================


# ------ Admission form document submittion serializers----------
# 1
class DocumentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ["label", "document"]


# 2
class DocumentSubmissionSerialiser(serializers.ModelSerializer):
    documents = DocumentItemSerializer(many=True, write_only=True)

    class Meta:
        model = DocumentFile
        fields = ["form_id", "school", "student", "documents"]

    from rest_framework.exceptions import ValidationError

    def create(self, validated_data):
        documents_data = validated_data.pop("documents")

        student = validated_data.get("student")
        form = validated_data.get("form_id")
        school = validated_data.get("school")

        # CASE 1: Documents already completed
        if student.details_done:
            raise ValidationError({"message": "Documents process already completed"})

        instances = []

        for doc in documents_data:
            label = doc.get("label")
            document = doc.get("document")

            # CASE 2: Update if already exists
            obj, created = DocumentFile.objects.update_or_create(
                student=student,
                label=label,  # 🔥 THIS makes it unique per document type
                defaults={"form_id": form, "school": school, "document": document},
            )

            instances.append(obj)

        return instances


# =======================================================================


class MobileCheckSerializer(serializers.Serializer):
    mobile = serializers.CharField()


# For viewing data


class StudentFieldValueReadSerializer(serializers.ModelSerializer):
    field_label = serializers.CharField(source="field.label")

    class Meta:
        model = StudentFieldValue
        fields = ["field_label", "value", "file"]


class FormSubmissionReadSerializer(serializers.ModelSerializer):
    field_values = StudentFieldValueReadSerializer(many=True)

    class Meta:
        model = Student
        fields = ["id", "created_at", "field_values"]


# Only for Post method
class SetDivisionSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(
        source="SchoolClass.get_school_class_display", read_only=True
    )

    class Meta:
        model = Division
        fields = ["id", "SchoolClass", "class_name", "division", "capacity"]


# =========serializers for set division by clerk========
# NOT IN USE
import string


class DivisionSetSerilaizer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(write_only=True)

    class Meta:
        model = Student
        fields = ["division", "capacity"]

    def create(self, validated_data):
        total_division = int(validated_data.pop("division"))
        capacity = validated_data.pop("capacity")

        alphabet = string.ascii_uppercase[:total_division]

        alphabet_len = len(alphabet)

        alphabet = list(string.ascii_uppercase[:alphabet_len])

        students = Student.objects.all().order_by("created_at")

        for index, student in enumerate(students):
            division = alphabet[index % alphabet_len]  # round-robin assignment
            student.division = division
            student.save()

        return students


# ==========CLERK UPDATE AND VERIFY DATA===============GET,PUT
# clerk side verify serializerfrom django.db import transaction


# =======================
# Field Value Serializer
# =======================
class StudentFieldValueReadSerializerForClerk(serializers.ModelSerializer):
    field_label = serializers.CharField(source="field.label", read_only=True)

    class Meta:
        model = StudentFieldValue
        fields = ["id", "field", "field_label", "value"]


# =======================
# Document Serializer
# =======================
class DocumentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ["id", "label", "document"]
        read_only_fields = ["id"]  # IMPORTANT FIX


# =======================
# Main Serializer
# =======================
class ClerkVerifySerializr(serializers.ModelSerializer):
    field_values = StudentFieldValueReadSerializerForClerk(many=True, required=False)
    documents = DocumentReadSerializer(many=True, required=False)

    class Meta:
        model = Student
        fields = [
            "id",
            "mobile",
            "school_class",
            "division",
            "clerk_verified",
            "clerk_verified_at",
            "gr_no",
            "documents",
            "field_values",
            "user",
            "school",
        ]
        read_only_fields = [
            "is_active",
            "details_done",
            "principle_verified",
            "principle_verified_at",
            "fees_verified",
            "fees_verified_at",
        ]

    def update(self, instance, validated_data):
        field_values_data = validated_data.pop("field_values", [])
        documents_data = validated_data.pop("documents", [])

        gr_no = validated_data.get("gr_no")
        mobile = validated_data.get("mobile")
        school = validated_data.get("school")

        # =========================
        # Update Student fields
        # =========================
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        with transaction.atomic():

            # ==================================================
            # 1. Create / assign Student User (safe check added)
            # ==================================================
            if not instance.user:
                student_user = User.objects.create(username=gr_no)
                student_user.set_password(gr_no)
                student_user.save()

                group, _ = Group.objects.get_or_create(name="student")
                student_user.groups.add(group)

                instance.user = student_user
                instance.save()

            # ==================================================
            # 2. Create Parent User (last 6 digits logic)
            # ==================================================
            last_six = str(mobile)[-6:]

            parent_user = User.objects.filter(username=last_six).first()
            if not parent_user:
                parent_user = User.objects.create(username=last_six)
                parent_user.set_password("123456")
                parent_user.save()

                group, _ = Group.objects.get_or_create(name="parents")
                parent_user.groups.add(group)

            # school_obj = School.objects.filter(id=school).first()

            Perents.objects.get_or_create(
                school=None, user=parent_user, perents_of=instance
            )

            # ==================================================
            # 3. FIELD VALUES (update or create)
            # ==================================================
            for field_data in field_values_data:
                StudentFieldValue.objects.update_or_create(
                    student=instance,
                    field_id=field_data.get("field"),
                    defaults={"value": field_data.get("value")},
                )

            # ==================================================
            # 4. DOCUMENTS (FIXED: no duplicates now)
            # ==================================================
            existing_docs = {doc.id: doc for doc in instance.documents.all()}

            for doc_data in documents_data:
                doc_id = doc_data.get("id")

                # UPDATE existing document
                if doc_id and doc_id in existing_docs:
                    doc = existing_docs[doc_id]
                    doc.label = doc_data.get("label", doc.label)

                    if doc_data.get("document") is not None:
                        doc.document = doc_data["document"]

                    doc.save()

                # CREATE new document
                else:
                    DocumentFile.objects.create(
                        student=instance,
                        label=doc_data.get("label"),
                        document=doc_data.get("document"),
                    )

        return instance


# ====================================================================


class PrincipleVerifySerializr(serializers.ModelSerializer):
    field_values = StudentFieldValueReadSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ["principle_verified", "principle_verified_at", "field_values"]


# =======set subject serializers========


class SetSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"
        read_only_fields = ["school"]


class SyllabusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Syllabus
        fields = "__all__"
        read_only_fields = ["school"]


class AssignClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignClass
        fields = "__all__"

    def create(self, validated_data):
        school = self.context["request"].user.school
        validated_data["school"] = school
        return super().create(validated_data)

# class Tt_daySerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = Tt_day
#         fields  = ['year','day','lecture','school_class']
#         read_only_fields = ['year']


class Tt_day_timeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tt_day_time
        fields = "__all__"
        read_only_fields = ["day"]


class Tt_breaksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tt_breaks
        fields = "__all__"
        read_only_fields = ["day"]


class Tt_slotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tt_slot
        fields = ["id", "lecture", "slot"]
        read_only_fields = ["id", "lecture"]


class SetTimeTableSerializer(serializers.ModelSerializer):
    year_value = serializers.CharField(source="year.year", read_only=True)
    division_name = serializers.CharField(source="class_div.division", read_only=True)
    class_name = serializers.CharField(
        source="class_div.SchoolClass.school_class", read_only=True
    )
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)

    class Meta:
        model = Time_table
        fields = [
            "id",
            "year",
            "year_value",
            "day",
            "class_div",
            "division_name",
            "class_name",
            "teacher",
            "teacher_name",
            "slot",
            "start",
            "end",
        ]


from django.db import transaction


class Tt_yearSerializer(serializers.ModelSerializer):
    start_year = serializers.IntegerField(write_only=True)
    end_year = serializers.IntegerField(write_only=True)

    class Meta:
        model = Tt_year
        fields = ["year", "start_year", "end_year"]

        read_only_fields = ["year"]

    def validate(self, data):
        start = data.get("start_year")
        end = data.get("end_year")

        if len(str(start)) != 4 or len(str(end)) != 4:
            raise serializers.ValidationError("Year must be 4 digits")

        if not (1900 <= start <= 2100):
            raise serializers.ValidationError(
                "Start year must be between 1900 and 2100"
            )

        if not (1900 <= end <= 2100):
            raise serializers.ValidationError("End year must be between 1900 and 2100")

        if end != start + 1:
            raise serializers.ValidationError("End year must be start_year + 1")

        return data

    def create(self, validated_data):
        start = validated_data.get("start_year")
        end = validated_data.get("end_year")

        year_str = f"{start}-{str(end)[-2:]}"

        request = self.context.get("request")
        school = getattr(getattr(request, "user", None), "school", None)

        if Tt_year.objects.filter(year=year_str).exists():
            raise serializers.ValidationError("This academic year already exists")

        with transaction.atomic():
            tt_year = Tt_year.objects.create(year=year_str, school=school)

        return tt_year


class Time_tableSerializer(serializers.ModelSerializer):
    year = serializers.PrimaryKeyRelatedField(
        queryset=Tt_year.objects.all(), write_only=True
    )

    day = serializers.CharField(write_only=True)
    lecture = serializers.CharField(write_only=True)

    class_div = serializers.PrimaryKeyRelatedField(
        queryset=Division.objects.all(), write_only=True, required=False
    )
    division = serializers.PrimaryKeyRelatedField(
        queryset=Division.objects.all(), write_only=True, required=False
    )

    day_time = Tt_day_timeSerializer(write_only=True)
    breaks = Tt_breaksSerializer(write_only=True, many=True)
    slot = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = Tt_year
        fields = [
            "id",
            "year",
            "day",
            "lecture",
            "class_div",
            "division",
            "day_time",
            "breaks",
            "slot",
        ]
        # read_only_fields = ["year"]

    def validate(self, data):
        slot_data = data.get("slot", [])
        class_div = data.get("class_div") or data.get("division")
        year = data.get("year")
        day = data.get("day")

        if not class_div:
            raise serializers.ValidationError({"class_div": "This field is required."})

        if year and day and class_div:
            if Tt_day.objects.filter(
                year=year,
                day=day,
                class_div=class_div,
            ).exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "This timetable already exists for the selected year, day and class division."
                        ]
                    }
                )

        for item in slot_data:
            if "slot" not in item or "start" not in item or "end" not in item:
                raise serializers.ValidationError(
                    "Each slot must have slot, start and end"
                )

        return data

    def create(self, validated_data):

        request = self.context.get("request")
        school = getattr(getattr(request, "user", None), "school", None)

        year = validated_data.pop("year")
        day = validated_data.pop("day")
        lecture = validated_data.pop("lecture")
        class_div = validated_data.pop("class_div", None) or validated_data.pop(
            "division", None
        )

        day_time_data = validated_data.pop("day_time")

        breaks_data = validated_data.pop("breaks")
        slot_data = validated_data.pop("slot", [])

        with transaction.atomic():

            tt_day = Tt_day.objects.create(
                school=school,
                year=year,
                day=day,
                class_div=class_div,
                lecture=lecture,
            )

            Tt_day_time.objects.create(
                school=school,
                day=tt_day,
                start=day_time_data.get("start"),
                end=day_time_data.get("end"),
            )

            for b in breaks_data:
                Tt_breaks.objects.create(
                    day=tt_day,
                    total_breaks=b.get("total_breaks"),
                    breaks=b.get("breaks"),
                    time=b.get("time"),
                    description=b.get("description"),
                )

            for item in slot_data:
                Tt_slot.objects.create(
                    school=school,
                    day=tt_day,
                    lecture=str(item.get("slot")),
                    slot={
                        "slot": item.get("slot"),
                        "start": item.get("start"),
                        "end": item.get("end"),
                    },
                )

        self._created_day_id = tt_day.id
        return year

    def to_representation(self, instance):
        request = self.context.get("request")
        days = instance.tt_day_set.all()

        class_div = request.query_params.get("class_div") if request else None
        class_id = request.query_params.get("class_id") if request else None

        if class_div:
            days = days.filter(class_div_id=class_div)

        if class_id:
            days = days.filter(class_div__SchoolClass_id=class_id)

        if request and request.method == "POST":
            created_day_id = getattr(self, "_created_day_id", None)
            if created_day_id:
                days = days.filter(id=created_day_id)

        data = {
            "id": instance.id,
            "year": instance.year,
            "days": [
                {
                    "id": d.id,
                    "day": d.day,
                    "lecture": d.lecture,
                    "class_div": (
                        {
                            "id": d.class_div.id,
                            "division": d.class_div.division,
                            "class_id": (
                                d.class_div.SchoolClass.id
                                if d.class_div and d.class_div.SchoolClass
                                else None
                            ),
                            "class_name": (
                                d.class_div.SchoolClass.school_class
                                if d.class_div and d.class_div.SchoolClass
                                else None
                            ),
                        }
                        if d.class_div
                        else None
                    ),
                    "day_time": (
                        {
                            "id": d.tt_day_time_set.first().id,
                            "start": str(d.tt_day_time_set.first().start),
                            "end": str(d.tt_day_time_set.first().end),
                        }
                        if d.tt_day_time_set.exists()
                        else None
                    ),
                    "breaks": [
                        {
                            "id": b.id,
                            "total_breaks": b.total_breaks,
                            "breaks": b.breaks,
                            "time": b.time,
                            "description": b.description,
                        }
                        for b in d.tt_breaks_set.all()
                    ],
                    "slot": [
                        {
                            "id": s.id,
                            "lecture": s.lecture,
                            "slot": s.slot,
                        }
                        for s in d.tt_slot_set.all()
                    ],
                }
                for d in days
            ],
        }

        if request and request.method == "POST":
            return {
                "message": "Table created successfully",
                "data": data,
            }

        return data


class GetStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student.objects.all()
        fields = []


class StudentFieldValueReadSerializerForPrinciple(serializers.ModelSerializer):
    field_label = serializers.CharField(source="field.label", read_only=True)

    class Meta:
        model = StudentFieldValue
        fields = ["id", "field", "field_label", "value"]


class GetStudentSerializer(serializers.ModelSerializer):
    field_values = StudentFieldValueReadSerializerForPrinciple(
        many=True, read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "mobile",
            "school",
            "form",
            "user",
            "mobile",
            "school_class",
            "division",
            "is_active",
            "created_at",
            "details_done",
            "principle_verified",
            "fees_verified",
            "clerk_verified",
            "principle_verified_at",
            "clerk_verified_at",
            "fees_verified_at",
            "gr_no",
            "field_values",
        ]

        read_only_fields = [
            "id",
            "field_values",
            "school",
            "form",
            "user",
            "mobile",
            "school_class",
            "division",
            "is_active",
            "created_at",
            "details_done",
            "principle_verified",
            "fees_verified",
            "clerk_verified",
            "principle_verified_at",
            "clerk_verified_at",
            "fees_verified_at",
            "gr_no",
            "field_values",
        ]


class AttendanceLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLocation
        fields = ["latitude", "longitude", "radius", "school", "start_time", "end_time", "half_day_time"]
        read_only_fields = ['school']

    def create(self, validated_data):
        request = self.context.get("request")
        
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")
        half_day_time = request.data.get("half_day_time")
        
        AttendanceTimeRule.objects.create(
            school=request.user.school,
            start_time=start_time,
            end_time=end_time,
            half_day_time=half_day_time
        )
        
        school = request.user.school
        
        
        
        return AttendanceLocation.objects.create(school=school, **validated_data)


import math


def is_inside_radius(lat1, lon1, lat2, lon2, radius_meters):
    R = 6371000

    def to_rad(deg):
        return deg * math.pi / 180

    dlat = to_rad(lat2 - lat1)
    dlon = to_rad(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))
    distance = R * c

    return distance <= radius_meters


class AttendanceSerializer(serializers.ModelSerializer):

    latitude = serializers.CharField(write_only=True)
    longitude = serializers.CharField(write_only=True)
    # radius = serializers.CharField(write_only=True)

    class Meta:
        model = Attendance
        fields = ["latitude", "longitude"]
        read_only_fields = [
            "school",
            "staff",
            "date_time",
            "name",
            "category",
            "is_present",
        ]

    def validate_latitude(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Latitude must be a valid number.")
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Longitude must be a valid number.")
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError(
                "Request user is required for attendance validation."
            )

        school = getattr(request.user, "school", None)
        if not school:
            raise serializers.ValidationError("User school is not configured.")

        attendance_location = AttendanceLocation.objects.filter(
            school=school.id
        ).first()
        if not attendance_location:
            raise serializers.ValidationError(
                "Attendance location is not configured for this school."
            )

        staff = Staff.objects.filter(user=request.user).first()
        if not staff:
            raise serializers.ValidationError(
                "Staff profile not found for current user."
            )

        today = timezone.now().date()
        if Attendance.objects.filter(staff=staff, date_time__date=today).exists():
            raise serializers.ValidationError(
                "Attendance has already been recorded for today."
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        school = request.user.school
        user = request.user

        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)

        attendance_location = AttendanceLocation.objects.filter(
            school=school.id
        ).first()
        loc_latitude = attendance_location.latitude
        loc_longitude = attendance_location.longitude
        loc_radius = attendance_location.radius

        is_inside = is_inside_radius(
            float(latitude),
            float(longitude),
            float(loc_latitude),
            float(loc_longitude),
            float(loc_radius),
        )

        if not is_inside:
            raise serializers.ValidationError(
                "You are not within the attendance radius."
            )

        staff = Staff.objects.filter(user=user).first()
        validated_data["staff"] = staff
        validated_data["school"] = school
        validated_data["category"] = staff.category
        # validated_data['name'] = staff.name

        validated_data["is_present"] = True
        validated_data["date_time"] = timezone.now()

        return Attendance.objects.create(**validated_data)


class LeaveTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTemplate
        fields = "__all__"
        read_only_fields = ["school"]

    def validate_leave_num(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Leave number must be a positive integer."
            )
        return value

    def validate_leave_type(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Leave type cannot be empty.")
        return value.strip()

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("Request user is required.")

        school = getattr(request.user, "school", None)
        if not school:
            raise serializers.ValidationError("User school is not configured.")

        leave_type = attrs.get("leave_type")
        time_line = attrs.get("time_line")

        # Check for duplicate leave templates for the same school
        if LeaveTemplate.objects.filter(
            school=school, leave_type=leave_type, time_line=time_line
        ).exists():
            raise serializers.ValidationError(
                "A leave template with this type and timeline already exists for this school."
            )

        return attrs

    def create(self, validated_data):
        school = self.context.get("request").user.school

        staff_data = Staff.objects.filter(school=school.id)

        leave_template = LeaveTemplate.objects.create(school=school, **validated_data)

        for staff in staff_data:
            StaffRemainingLeave.objects.create(
                school=school,
                leave_template=leave_template,
                staff=staff,
                total_levaes=validated_data.get("leave_num", 0),
                remaining_leaves=validated_data.get("leave_num", 0),
            )

        return leave_template


# ADD SERIALIZE FOR LEAVE DROWPOWN IN THROUGH LeaveTemplate MODEL
from datetime import timedelta


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = "__all__"
        read_only_fields = ["school", "staff", "total_days", "approved_by"]

    def create(self, validated_data):
        start_date = validated_data.get("start_date")
        end_date = validated_data.get("end_date")
        school = self.context.get("request").user.school
        user = self.context.get("request").user

        if end_date < start_date:
            raise serializers.ValidationError("End date cannot be before start date.")

        # ✅ calculate total days
        total_days = (end_date - start_date).days + 1
        validated_data["total_days"] = total_days
        validated_data["school"] = school

        staff = Staff.objects.filter(user=user, school=school).first()
        validated_data["staff"] = staff

        # ✅ create main LeaveRequest first
        leave_request = LeaveRequest.objects.create(**validated_data)

        # ✅ now create LeavePerDay entries
        current = start_date
        while current <= end_date:
            LeavePerDay.objects.create(
                school=school,
                leave=leave_request,  # ✅ correct instance
                date=current,  # store as DateField (recommended)
            )
            current += timedelta(days=1)

        return leave_request


class StaffRemainingLeaveSerializer(serializers.ModelSerializer):
    leave_type = serializers.CharField(
        source="leave_template.leave_type", read_only=True
    )

    class Meta:
        model = StaffRemainingLeave
        fields = ["id", "staff", "leave_type", "total_levaes", "remaining_leaves"]
        read_only_fields = ["id"]


class GetLeavePerDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePerDay
        fields = ["id", "date", "school", "leave", "status", "approved_at"]
        read_only_fields = ["id", "date", "school", "leave"]


class GetLeaveRequestSerializer(serializers.ModelSerializer):
    leave_days = GetLeavePerDaySerializer(many=True, read_only=True)
    remaining_leaves = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "staff",
            "leave_type",
            "reason",
            "total_days",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
            "leave_days",
            "remaining_leaves",
        ]
        read_only_fields = [
            "school",
            "staff",
            "leave_type",
            "total_days",
            "leave_days",
            "remaining_leaves",
        ]

    def get_remaining_leaves(self, obj):
        queryset = StaffRemainingLeave.objects.filter(
            staff=obj.staff, school=obj.school
        )
        return StaffRemainingLeaveSerializer(queryset, many=True).data


from django.db.models import F


class ChangeLeavePerDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePerDay
        fields = ["status"]

    def validate_status(self, value):
        valid_statuses = ["PENDING", "APPROVED", "REJECTED", "CANCELLED"]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Valid options are: {', '.join(valid_statuses)}"
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("Request user is required.")

        new_status = attrs.get("status")
        instance = self.instance

        # ✅ Check if status is already in a final state
        if instance.status in ["CANCELLED"]:
            raise serializers.ValidationError(
                f"Cannot change status from {instance.status}. This leave is already finalized."
            )

        # ✅ Check invalid transitions
        if instance.status == "REJECTED" and new_status in ["APPROVED"]:
            raise serializers.ValidationError("Cannot approve a rejected leave.")

        # ✅ If changing to APPROVED, validate remaining leaves
        if new_status == "APPROVED" and instance.status != "APPROVED":
            leave_request = instance.leave
            staff = leave_request.staff
            leave_type = leave_request.leave_type

            remaining_data = StaffRemainingLeave.objects.filter(
                leave_template__leave_type=leave_type, staff=staff
            ).first()

            if not remaining_data:
                raise serializers.ValidationError(
                    f"No leave template found for {leave_type}."
                )

            if remaining_data.remaining_leaves <= 0:
                raise serializers.ValidationError(
                    f"Insufficient {leave_type} leaves. Remaining: {remaining_data.remaining_leaves}"
                )

        return attrs

    def update(self, instance, validated_data):
        user = self.context["request"].user
        new_status = validated_data.get("status")
        old_status = instance.status

        leave_request = instance.leave
        staff = leave_request.staff
        leave_type = leave_request.leave_type

        remaining_data = StaffRemainingLeave.objects.filter(
            leave_template__leave_type=leave_type, staff=staff
        ).first()

        # ✅ Case 1: PENDING/REJECTED → APPROVED (consume leaves)
        if new_status == "APPROVED" and old_status != "APPROVED":
            if remaining_data:
                remaining_data.remaining_leaves -= 1
                remaining_data.save()
            instance.approved_at = timezone.now()

        # ✅ Case 2: APPROVED → REJECTED/CANCELLED (restore leaves)
        elif old_status == "APPROVED" and new_status in ["REJECTED", "CANCELLED"]:
            if remaining_data:
                remaining_data.remaining_leaves += 1
                remaining_data.save()
            instance.approved_at = None

        # ✅ Case 3: Any other transition to REJECTED/CANCELLED (no leaves to restore)
        elif new_status in ["REJECTED", "CANCELLED"]:
            instance.approved_at = None

        instance.status = new_status
        instance.save()

        return instance


# class
class GetRemainingLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffRemainingLeave
        fields = ["leave_template"]


class AnnouncementTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementTarget
        fields = "__all__"
        read_only_fields = ["school","announcement"]

class AnnouncementSerializer(serializers.ModelSerializer):
    targets = AnnouncementTargetSerializer(many=True, required=False)
    class Meta:
        model = Announcement
        fields = ["id", "title", "description", "publish_at", "expires_at", "targets", "school"]
        read_only_fields = ["school"]
        
        
    def create(self, validated_data):
        targets_data = validated_data.pop("targets", [])
        user = self.context["request"].user 
        
        print(targets_data)
        
        announcement = Announcement.objects.create(school=user.school, **validated_data)
        
        for target_data in targets_data:
            AnnouncementTarget.objects.create( school=user.school, announcement=announcement, **target_data)
        
        return announcement
    


class GetAnnouncementSerializer(serializers.ModelSerializer):
    targets = AnnouncementTargetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Announcement
        fields = ["id", "title", "description", "publish_at", "expires_at", "targets"]
        
