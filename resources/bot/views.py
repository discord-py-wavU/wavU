from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework_api_key.permissions import HasAPIKey

from config import client


class CountServer(APIView):

    def get(self, request):
        import ipdb; ipdb.set_trace()
        return Response(len(client.guilds))
