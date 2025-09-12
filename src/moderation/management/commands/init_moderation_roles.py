from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from moderation.models import ProductProposal

class Command(BaseCommand):
    help = "Создаёт группу 'moderators' и выдаёт права на ProductProposal."

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="moderators")
        ct = ContentType.objects.get_for_model(ProductProposal)
        perms = Permission.objects.filter(content_type=ct)
        group.permissions.add(*perms)
        self.stdout.write(self.style.SUCCESS("Группа 'moderators' и права настроены."))