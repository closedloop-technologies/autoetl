import logging
import requests
from typing import Dict, List, Any, Optional
from entity_types import EntityType
from auth_rbac import determine_auth_rbac
from swagger_parser import parse_swagger_spec

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(
        self, base_url: str, swagger_spec: List[Dict], entity_types: List[EntityType]
    ):
        self.base_url = base_url
        self.swagger_spec = swagger_spec
        self.entity_types = entity_types
        self.auth_details = determine_auth_rbac(swagger_spec)["auth_details"]
        self.rbac_mapping = determine_auth_rbac(swagger_spec)["rbac_mapping"]

    def _authenticate(self) -> Dict[str, str]:
        # TODO: Implement authentication based on the auth_details
        return {}

    def _authorize(self, endpoint: str, method: str) -> bool:
        # TODO: Implement authorization based on the rbac_mapping
        return True

    def _validate_request(
        self, endpoint: str, method: str, request_data: Dict[str, Any]
    ) -> bool:
        # TODO: Validate the request data against the request type for the endpoint
        return True

    def _handle_response(
        self, response: requests.Response, endpoint: str, method: str
    ) -> Optional[EntityType]:
        # TODO: Handle the response data and validate it against the response type for the endpoint
        return None

    def _make_request(
        self, endpoint: str, method: str, request_data: Dict[str, Any]
    ) -> Optional[EntityType]:
        if not self._authorize(endpoint, method):
            logger.error(
                f"Authorization failed for endpoint: {endpoint}, method: {method}"
            )
            return None

        if not self._validate_request(endpoint, method, request_data):
            logger.error(
                f"Invalid request data for endpoint: {endpoint}, method: {method}"
            )
            return None

        headers = self._authenticate()
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(method, url, json=request_data, headers=headers)
            response.raise_for_status()
            return self._handle_response(response, endpoint, method)
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Error making request to endpoint: {endpoint}, method: {method}, error: {e}"
            )
            return None

    def paginated_request(
        self,
        endpoint: str,
        method: str,
        request_data: Dict[str, Any],
        page_size: int = 50,
        page_number: int = 1,
    ) -> List[EntityType]:
        # TODO: Implement pagination logic
        return []

    def __getattr__(self, item: str) -> Any:
        # Dynamically generate methods for each API endpoint
        for endpoint_info in self.swagger_spec:
            path = endpoint_info["path"]
            method = endpoint_info["method"]
            endpoint_name = f"{path}_{method}".replace("/", "_")

            if item == endpoint_name:

                def _request(
                    request_data: Dict[str, Any] = None
                ) -> Optional[EntityType]:
                    return self._make_request(path, method, request_data or {})

                return _request

        raise AttributeError(f"Endpoint not found: {item}")
