from django.core.management.base import BaseCommand
from domains.models import TechDomain
from accounts.models import User

class Command(BaseCommand):
    help = 'Create default tech domains'

    def handle(self, *args, **options):
        default_domains = [
            {
                'name': 'Cybersecurity',
                'description': 'Ethical hacking, penetration testing, security analysis',
                'icon': 'fas fa-shield-alt'
            },
            {
                'name': 'Backend Development',
                'description': 'Server-side development, APIs, databases',
                'icon': 'fas fa-server'
            },
            {
                'name': 'Frontend Development',
                'description': 'UI/UX, React, Vue, responsive design',
                'icon': 'fas fa-paint-brush'
            },
            {
                'name': 'Mobile Development',
                'description': 'Android, iOS, React Native, Flutter',
                'icon': 'fas fa-mobile-alt'
            },
            {
                'name': 'AI & Machine Learning',
                'description': 'Deep learning, data science, neural networks',
                'icon': 'fas fa-robot'
            },
            {
                'name': 'DevOps & Cloud',
                'description': 'AWS, Docker, Kubernetes, CI/CD',
                'icon': 'fas fa-cloud'
            },
        ]
        
        # Get first admin user or create one
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(role='admin').first()
        
        if not admin_user:
            self.stdout.write(
                self.style.WARNING('No admin user found. Please create domains manually.')
            )
            return
        
        for domain_data in default_domains:
            domain, created = TechDomain.objects.get_or_create(
                name=domain_data['name'],
                defaults={
                    'description': domain_data['description'],
                    'icon': domain_data['icon'],
                    'created_by': admin_user,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created domain: {domain.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Domain already exists: {domain.name}')
                )
