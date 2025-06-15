from smtplib import SMTPException
from django.core.management.base import BaseCommand
from datetime import date, datetime, timedelta
from accounts.models import User
from progress.models import Goal, GoalTask, WeeklyProgressReport
from domains.models import TechDomain, UserDomain
import random
from progress import utils

class Command(BaseCommand):
    help = 'Generate weekly progress reports for all users'

    def handle(self, *args, **options):
        # today = date.today()
        # week_start = today - timedelta(days=today.weekday())
        
        # week_end = week_start + timedelta(days=6)
        
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        motivational_messages = [
            "Great effort this week! Your consistency is paying off.",
            "You're making solid progress. Keep up the momentum!",
            "Impressive dedication! Your skills are definitely growing.",
            "Nice work! Consider sharing your progress with the community.",
            "Consistent progress detected—you're on the right track!",
        ]
        
        suggestions = [
            "Try building a mini project to apply your knowledge.",
            "Consider teaming up with a peer for your next challenge.",
            "Set a slightly more challenging goal for next week.",
            "Connect with a mentor in your domain for guidance.",
        ]
        
        for user in User.objects.filter(is_profile_complete=True):
            
            if WeeklyProgressReport.objects.filter(
                user=user, 
                week_start=now
            ).exists():
                self.stdout.write(f'Skipping {user.username} - report already exists for this minute')
                continue
            
            goals_completed = Goal.objects.filter(
                user=user,
                completed_at__range=[one_minute_ago, now]
            ).count()
            
            tasks_completed = GoalTask.objects.filter(
                goal__user=user,
                # completed_at__date__range=[week_start, week_end]
                completed_at__range=[one_minute_ago, now]
            ).count()
            
            active_domains = TechDomain.objects.filter(
                userdomain__user=user,
                userdomain__is_active=True
            )
            
            report = WeeklyProgressReport.objects.create(
                user=user,
                week_start=now,#week_start,
                week_end=one_minute_ago,#week_end,
                goals_completed=goals_completed,
                tasks_completed=tasks_completed,
                motivational_message=random.choice(motivational_messages),
                suggestions=random.choice(suggestions)
            )
            
            report.domains_active.set(active_domains)
            
            try:
                utils.send_weekly_motivation_email(user, report)
                self.stdout.write(
                    self.style.SUCCESS(f'Generated report and sent email for {user.username}')
                )
            except (SMTPException, ConnectionError, OSError, AttributeError) as e:
                self.stdout.write(
                    self.style.ERROR(f'Generated report for {user.username} but failed to send email: {str(e)}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Generated report for {user.username} but unexpected error occurred: {str(e)}')
                )
