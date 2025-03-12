from django.contrib.auth.models import AbstractUser # type: ignore
from django.db import models # type: ignore


class CustomUser(AbstractUser):
    is_subadmin = models.BooleanField(default=False)
    groups = models.ManyToManyField('auth.Group', related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_set', blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.is_superuser:
            self.is_subadmin = True
        super().save(*args, **kwargs)

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.email} generated at {self.timestamp}"

class new_user(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('job_seeker', 'Job Seeker'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    firstname=models.CharField(max_length=20)
    lastname=models.CharField(max_length=20)
    country_code=models.CharField(max_length=5,default='IN')
    phonenumber=models.CharField(max_length=10)
    email=models.EmailField()
    password=models.CharField(max_length=100)
    course=models.CharField(max_length=50,default='B-Tech')
    educations=models.CharField(max_length=20,default='Not specified')
    percentage=models.CharField(max_length=10,default='0')
    preferred_destination=models.CharField(max_length=20,default='Not specified')
    start_date = models.CharField(max_length=4)
    entrance=models.CharField(max_length=5,default='N/A')
    passport=models.CharField(max_length=5,default='None')
    mode_study=models.CharField(max_length=20,default='None')
    job_experience = models.CharField(max_length=100, blank=True, null=True)
    desired_job_title = models.CharField(max_length=100, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=True)


class Meta:
    db_table="collegecuefinal_data"

class CompanyInCharge(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    company_name = models.CharField(max_length=255,default="null")
    official_email = models.EmailField(unique=True,default="Null")
    country_code = models.CharField(max_length=3, default='+91')
    mobile_number = models.CharField(max_length=15,default="Null")
    password = models.CharField(max_length=128,default="null")
    linkedin_profile = models.URLField(blank=True, null=True)
    company_person_name = models.CharField(max_length=255,default="Null")
    agreed_to_terms = models.BooleanField(default=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    # otp_code = models.CharField(max_length=6, blank=True, null=True)
    # otp_generated_at = models.DateTimeField(blank=True, null=True)

    # def is_otp_valid(self):
    #     if self.otp_generated_at:
    #         return now() <= self.otp_generated_at + timedelta(minutes=10)
    #     return False



class UniversityInCharge(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    clg_id = models.CharField(max_length=400, default="Null", blank=True, null=True)
    university_name = models.CharField(max_length=255)
    official_email = models.EmailField(unique=True,default="Null")
    country_code = models.CharField(max_length=3, default='+91')
    mobile_number = models.CharField(max_length=15,default="Null")
    password = models.CharField(max_length=128,default="null")
    linkedin_profile = models.URLField(blank=True, null=True)
    college_person_name = models.CharField(max_length=255,default="Null")
    agreed_to_terms = models.BooleanField(default=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    # trimmed_university_name = models.CharField(max_length=255, default='N/A')
    # otp_code = models.CharField(max_length=6, blank=True, null=True)
    # otp_generated_at = models.DateTimeField(blank=True, null=True)

    # def is_otp_valid(self):
    #     if self.otp_generated_at:
    #         return now() <= self.otp_generated_at + timedelta(minutes=10)
    #     return False


class Consultant(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    consultant_name = models.CharField(max_length=255,default="Null")
    official_email = models.EmailField(unique=True,default="Null")
    country_code = models.CharField(max_length=3, default='+91')
    mobile_number = models.CharField(max_length=15,default="Null")
    password = models.CharField(max_length=128,default="null")
    linkedin_profile = models.URLField(blank=True, null=True)
    consultant_person_name = models.CharField(max_length=255,default="Null")
    agreed_to_terms = models.BooleanField(default=True)
    token = models.CharField(max_length=255, blank=True, null=True)

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.email

class Forgot(models.Model):
    email = models.EmailField(unique=False)

class Verify(models.Model):
    otp=models.CharField(max_length=4)

class Forgot2(models.Model):
    password=models.CharField(max_length=12)
    confirm_password=models.CharField(max_length=12)

class Subscriber1(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

class JobSeeker(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    country_code = models.CharField(max_length=5)
    token = models.CharField(max_length=255, blank=True, null=True)
    agreed_to_terms = models.BooleanField(default=True)
    # otp_code = models.CharField(max_length=6, blank=True, null=True)
    # otp_generated_at = models.DateTimeField(blank=True, null=True)

    # def is_otp_valid(self):
    #     if self.otp_generated_at:
    #         return now() <= self.otp_generated_at + timedelta(minutes=10)
    #     return False


    def __str__(self):
      return f"{self.first_name} {self.last_name}"

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Question(models.Model):
    text = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

class AdmissionReview1(models.Model):
    college_name = models.CharField(max_length=255)
    other_college_name = models.CharField(max_length=255, blank=True, null=True)
    course_name = models.CharField(max_length=255)
    other_course_name = models.CharField(max_length=255, blank=True, null=True)
    student_name = models.CharField(max_length=255)
    email = models.EmailField()
    country_code=models.CharField(max_length=5,default='IN')
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    linkedin_profile = models.URLField(blank=True, null=True)
    course_fees = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.IntegerField()
    referral_code = models.CharField(max_length=50, blank=True, null=True)
    apply = models.CharField(max_length=20, default='applied')
    anvil_reservation_benefits = models.BooleanField()
    benefit = models.CharField(max_length=20, default='Benefits')
    gd_pi_admission = models.BooleanField()
    class_size = models.IntegerField()
    opted_hostel = models.BooleanField()
    college_provides_placements = models.BooleanField()
    hostel_fees = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    average_package = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    admission_process = models.TextField()
    course_curriculum_faculty = models.TextField()
    fees_structure_scholarship = models.TextField()
    liked_things = models.TextField()
    disliked_things = models.TextField()

    # File fields instead of URL fields
    profile_photo = models.FileField(upload_to='uploads/profile_photos/', blank=True, null=True)
    campus_photos = models.FileField(upload_to='uploads/campus_photos/', blank=True, null=True)
    certificate_id_card = models.FileField(upload_to='uploads/certificates/', blank=True, null=True)
    graduation_certificate = models.FileField(upload_to='uploads/graduation_certificates/', blank=True, null=True)


    agree_terms = models.BooleanField(default=True)
    
class UnregisteredColleges(models.Model):
    university_name = models.CharField(max_length=255)
    official_email = models.EmailField(unique=True,default="Null")
    country_code = models.CharField(max_length=3, default='+91')
    mobile_number = models.CharField(max_length=15,default="Null")
    password = models.CharField(max_length=128,default="null")
    linkedin_profile = models.URLField(blank=True, null=True)
    college_person_name = models.CharField(max_length=255,default="Null")
    agreed_to_terms = models.BooleanField(default=True)