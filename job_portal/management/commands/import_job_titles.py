import pandas as pd # type: ignore
from django.core.management.base import BaseCommand
from job_portal.models import Application, Job, Company
from login.models import CompanyInCharge

class Command(BaseCommand):
    help = 'Import data from multiple Excel files to the Job, Company, and Application models'

    def add_arguments(self, parser):
        file_fields = [
            ('job_title', 'Path to the Excel file containing job titles'),
            ('job_type', 'Path to the Excel file containing job types'),
            ('exp_type', 'Path to the Excel file containing job experience'),
            ('category_type', 'Path to the Excel file containing job categories'),
            ('workplace_types', 'Path to the Excel file containing workplace types'),
            ('location_types', 'Path to the Excel file containing job locations'),
            ('sector_type', 'Path to the Excel file containing sector types'),
            ('country_type', 'Path to the Excel file containing country names'),
            ('application_status', 'Path to the Excel file containing application statuses')
        ]
        for arg, help_text in file_fields:
            parser.add_argument(arg, type=str, help=help_text)

    def handle(self, *args, **kwargs):
        job_titles_path = kwargs['job_title']
        job_types_path = kwargs['job_type']
        experience_path = kwargs['exp_type']
        categories_path = kwargs['category_type']
        workplace_types_path = kwargs['workplace_types']
        locations_path = kwargs['location_types']
        sector_types_path = kwargs['sector_type']
        country_names_path = kwargs['country_type']
        statuses_path = kwargs['application_status']

        try:
            job_titles_df = pd.read_excel(job_titles_path)
            job_types_df = pd.read_excel(job_types_path)
            experience_df = pd.read_excel(experience_path)
            categories_df = pd.read_excel(categories_path)
            workplace_types_df = pd.read_excel(workplace_types_path)
            locations_df = pd.read_excel(locations_path)
            sector_types_df = pd.read_excel(sector_types_path)
            country_names_df = pd.read_excel(country_names_path)
            statuses_df = pd.read_excel(statuses_path)

            company_in_charge, _ = CompanyInCharge.objects.get_or_create(company_name="Default CompanyInCharge")

            max_rows = max(
                len(job_titles_df),
                len(job_types_df),
                len(experience_df),
                len(categories_df),
                len(workplace_types_df),
                len(locations_df),
                len(sector_types_df),
                len(country_names_df),
                len(statuses_df)
            )

            for i in range(max_rows):
                job_title = job_titles_df.iloc[i]['job_title'] if i < len(job_titles_df) else ''
                job_type = job_types_df.iloc[i]['job_type'] if i < len(job_types_df) else ''
                experience = experience_df.iloc[i]['experience'] if i < len(experience_df) else ''
                category = categories_df.iloc[i]['category'] if i < len(categories_df) else ''
                workplace_type = workplace_types_df.iloc[i]['workplaceTypes'] if i < len(workplace_types_df) else ''
                location = locations_df.iloc[i]['location'] if i < len(locations_df) else ''
                sector_type = sector_types_df.iloc[i]['sector_type'] if i < len(sector_types_df) else ''
                country = country_names_df.iloc[i]['country_name'] if i < len(country_names_df) else ''
                status = statuses_df.iloc[i]['status'] if i < len(statuses_df) else ''

                if sector_type or country:
                   company, _= Company.objects.get_or_create(
                       company_in_charge=company_in_charge,
                        sector_type=sector_type,
                        country=country
                    )

                if job_title or job_type or experience or category or workplace_type or location:
                    job, _= Job.objects.get_or_create(
                        company_in_charge=company_in_charge,
                        job_title=job_title,
                        job_type=job_type,
                        experience=experience,
                        category=category,
                        workplaceTypes=workplace_type,
                        location=location,
                        company=company

                    )

                if job and status:
                    Application.objects.create(
                        company_in_charge=company_in_charge,
                        job=job,
                        status=status,
                    )

                self.stdout.write(self.style.SUCCESS(f'Successfully imported row {i+1}'))

        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'File not found: {e.filename}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))