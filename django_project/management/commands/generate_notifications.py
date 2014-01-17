from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User, Group

from notifications import notify
from notifications.models import Notification

from django_project import signals
from django_project.models import Task, Project
from follow.models import Follow

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        Notification.objects.all().delete()
        for obj in list(Task.objects.all()) + list(Project.objects.all()) + list(User.objects.all()) + list(Group.objects.all()):
            for follow in Follow.objects.get_follows(obj):
                print(follow.user, follow.target)
                print('-'*70)

                signals.follow.send(Command, follower=follow.user, followee=obj)
