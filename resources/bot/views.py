from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework_api_key.permissions import HasAPIKey

from config import client


class CountServer(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    def post(self, request):
        return Response(len(client.guilds))
