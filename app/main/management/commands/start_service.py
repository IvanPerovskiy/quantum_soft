from django.core.management.base import BaseCommand
from django.db import transaction

from main.utils import start_service


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with transaction.atomic():
            start_service()
