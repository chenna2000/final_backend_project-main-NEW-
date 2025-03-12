from django import forms # type: ignore
from .models import Achievements, Advertisement, Application, Application1, Certification, College, CollegeAdvertisement, CollegeMembership, Education, JobSeeker_Achievements, JobSeeker_Certification, JobSeeker_Education, JobSeeker_Experience, JobSeeker_Objective, JobSeeker_Project, JobSeeker_Publications, JobSeeker_Reference, JobSeeker_Resume,Experience, Job, Company, Job1, Membership, Objective, Project, Publications, Reference, Resume, Student, Visitor

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_title', 'company', 'location', 'description',
                   'requirements', 'job_type', 'experience', 'category',
                     'skills', 'experience_yr', 'workplaceTypes','questions','job_status',
                     ]
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
        }

class ApplicationForm(forms.ModelForm):

    resume = forms.FileField(required=False)
    cover_letter = forms.CharField(required=False)
    skills = forms.CharField(required=False)

    class Meta:
        model = Application
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'resume', 'cover_letter', 'skills']

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'email','phone','address', 'city', 'state','country', 'zipcode', 'website', 'website_urls' ,'about_company','sector_type','category','established_date','employee_size']

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['first_name','last_name', 'email', 'phone', 'address', 'date_of_birth', 'website_urls', 'skills', 'activities', 'interests', 'languages','bio','city','state','country','zipcode']

class ObjectiveForm(forms.ModelForm):
    class Meta:
        model = Objective
        fields = ['text']

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['course_or_degree', 'school_or_university', 'grade_or_cgpa', 'start_date', 'end_date','description']

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'company_name', 'start_date', 'end_date', 'description']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description','project_link']

class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['name', 'contact_info', 'relationship']

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name','start_date','end_date']

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievements
        fields = ['title','publisher','start_date','end_date']

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publications
        fields = ['title', 'publisher', 'start_date','end_date']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'contact_no', 'qualification','skills']

class Job1Form(forms.ModelForm):
    class Meta:
        model = Job1
        fields = ['job_title', 'college', 'location', 'description',
                   'requirements', 'job_type', 'experience', 'category',
                     'skills', 'experience_yr', 'workplaceTypes','questions','job_status',
                    ]
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
        }

class Application1Form(forms.ModelForm):
    class Meta:
        model = Application1
        fields = ['first_name','last_name', 'email', 'phone_number', 'resume', 'cover_letter', 'skills']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
        }

class CollegeForm(forms.ModelForm):
    class Meta:
        model = College
        fields = ['college_name', 'email','website','phone', 'founded_date', 'university_type','about_college', 'website_urls','address','city','state','country','zipcode']

class VisitorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'password']

class JobseekerResumeForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Resume
        fields = ['first_name','last_name', 'email', 'phone', 'address', 'date_of_birth', 'website_urls', 'skills', 'activities', 'interests', 'languages','bio','city','state','country','zipcode']

class JobseekerObjectiveForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Objective
        fields = ['text']

class JobseekerEducationForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Education
        fields = ['course_or_degree', 'school_or_university', 'grade_or_cgpa', 'start_date', 'end_date','description']

class JobseekerExperienceForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Experience
        fields = ['job_title', 'company_name', 'start_date', 'end_date', 'description']

class JobseekerProjectForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Project
        fields = ['title', 'description','project_link']

class JobseekerReferenceForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Reference
        fields = ['name', 'contact_info', 'relationship']

class JobseekerCertificationForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Certification
        fields = ['name','start_date','end_date']

class JobseekerAchievementForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Achievements
        fields = ['title','publisher','start_date','end_date']

class JobseekerPublicationForm(forms.ModelForm):
    class Meta:
        model = JobSeeker_Publications
        fields = ['title', 'publisher', 'start_date','end_date']

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['name', 'email', 'mobile', 'course_to_purchase', 'quantity_of_leads', 'location_for_leads', 'intake_year']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter your mobile number'}),
            'course_to_purchase': forms.TextInput(attrs={'placeholder': 'Enter course name'}),
            'quantity_of_leads': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'location_for_leads': forms.TextInput(attrs={'placeholder': 'Enter location'}),
            'intake_year': forms.NumberInput(attrs={'placeholder': 'Enter intake year'}),
        }

class MembershipForm1(forms.ModelForm):
    class Meta:
        model = CollegeMembership
        fields = ['name', 'email', 'mobile', 'course_to_purchase', 'quantity_of_leads', 'location_for_leads', 'intake_year']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter your mobile number'}),
            'course_to_purchase': forms.TextInput(attrs={'placeholder': 'Enter course name'}),
            'quantity_of_leads': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'location_for_leads': forms.TextInput(attrs={'placeholder': 'Enter location'}),
            'intake_year': forms.NumberInput(attrs={'placeholder': 'Enter intake year'}),
        }

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['name', 'email', 'contact', 'advertisement_placement', 'time_duration', 'investment_cost', 'target_audience']

class AdvertisementForm1(forms.ModelForm):
    class Meta:
        model = CollegeAdvertisement
        fields = ['name', 'email', 'contact', 'advertisement_placement', 'time_duration', 'investment_cost', 'target_audience']


