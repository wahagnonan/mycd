import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Matiere


class Command(BaseCommand):
    help = "Charge les données de seed (matières, communes) dans la base"

    DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data"

    def handle(self, *args, **options):
        self._load_matieres()
        self.stdout.write(self.style.SUCCESS("Données de seed chargées avec succès."))

    @transaction.atomic
    def _load_matieres(self):
        path = self.DATA_DIR / "matieres.json"
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"Fichier {path} introuvable. Ignoré."))
            return

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        created = 0
        for item in data:
            _, is_new = Matiere.objects.get_or_create(nom=item["nom"])
            if is_new:
                created += 1

        self.stdout.write(f"  Matières : {created} créée(s), {Matiere.objects.count()} totale(s)")
