import json
from pathlib import Path

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


DATA_DIR = Path(settings.BASE_DIR) / "data"


@api_view(["GET"])
@permission_classes([AllowAny])
def ville_list(request):
    path = DATA_DIR / "communes.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    villes = [{"ville": item["ville"], "quartiers": item["quartiers"]} for item in data]
    return Response(villes)
