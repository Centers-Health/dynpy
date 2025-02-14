from typing import Dict

import requests
from django.conf import settings
from django.http import HttpRequest

from dynpy.graphql.users import get_internal_api_user
from dynpy.strawberry_django_jwt.settings import jwt_settings
from dynpy.utils.objects import get_attribute


class GraphConnector:
    url = settings.GRAPH_URL

    verify = settings.DJANGO_ENV == "prod"

    def __init__(self, request=None) -> None:
        self.request = request

    def execute(self, gql: str, variables: Dict = {}, timeout=10) -> Dict:
        """
        Wrapper for request to GraphQl endpoint.
        Takes in a query and variables and passes them along to the request.
        """
        data = {"query": gql, "variables": variables}

        response = requests.post(
            self.url,
            json=data,
            verify=self.verify,
            timeout=timeout,
            cookies=self._get_cookies(),
        )
        if not response.ok:
            raise response.raise_for_status()

        return response.json()

    def _get_cookies(self):
        cookies = {}
        if get_attribute(self.request, "user", "is_authenticated"):
            cookies.update({jwt_settings.JWT_COOKIE_NAME: self._get_JWT()})
        return cookies

    def _get_JWT(self):
        payload = jwt_settings.JWT_PAYLOAD_HANDLER(self.request.user)
        return jwt_settings.JWT_ENCODE_HANDLER(payload)


class SuperuserGraphConnector(GraphConnector):
    def __init__(self) -> None:
        request = HttpRequest()
        request.user = get_internal_api_user()
        super().__init__(request)
