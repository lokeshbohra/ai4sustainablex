"""
ai4sustainablex — Abstract Base Connector Class
Implements an MCP-style (Model-Connector-Plugin) interface for extensible data sources.
All third-party connectors inherit from this base.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ConnectorType(Enum):
    """Supported connector categories."""
    SEARCH = "search"           # Web search engines
    DATA_API = "data_api"       # ESG data APIs (SustainableX data)
    TEMPLATE_LIBRARY = "template_library"  # SustainableX template library
    LLM_PROVIDER = "llm_provider"  # LLM inference providers
    DOCUMENT = "document"       # Document/File connectors
    CUSTOM = "custom"           # User-defined plugins


@dataclass
class ConnectorConfig:
    """Configuration for a connector instance."""
    name: str
    connector_type: ConnectorType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    rate_limit: int = 60        # Requests per minute
    timeout: int = 30           # Seconds


class BaseConnector(ABC):
    """
    Abstract base for all connectors in ai4sustainablex.

    Implements the MCP-style tool interface:
    - authenticate(): Validate credentials and establish connection
    - fetch(): Retrieve data from the source
    - search(): Perform a search query
    - get_templates(): Return available report templates (for template connectors)
    - health_check(): Verify the connector is operational
    - validate_key(): Check if the provided API key is valid
    """

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self._authenticated = False
        self._session = None

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the external data source.
        Returns True if authentication succeeded.
        """
        ...

    @abstractmethod
    def fetch(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch data from a specific endpoint.

        Args:
            endpoint: The API endpoint or resource path
            params: Query parameters for the request

        Returns:
            Dictionary containing the fetched data
        """
        ...

    @abstractmethod
    def search(self, query: str, top_k: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for documents or data matching the query.

        Args:
            query: The search query string
            top_k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of result dictionaries with keys: title, url, snippet, source
        """
        ...

    def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve available report templates.

        Args:
            category: Optional filter by template category
                     (e.g., 'GRI', 'SBTi', 'CDP', 'IFRS', 'CSRD', 'AFOLU')

        Returns:
            List of template metadata dictionaries
        """
        return []

    def health_check(self) -> bool:
        """
        Verify the connector is operational.
        Default implementation checks if authentication was successful.
        """
        return self._authenticated

    def validate_key(self) -> Dict[str, Any]:
        """
        Validate the API key and return status information.

        Returns:
            Dict with keys: valid (bool), message (str), tier (str), remaining_quota (int)
        """
        return {
            "valid": self._authenticated,
            "message": "Authentication status unknown",
            "tier": "free",
            "remaining_quota": 0,
        }

    def get_config_schema(self) -> Dict[str, Any]:
        """
        Return the configuration schema for this connector.
        Used by the setup wizard to know what fields to prompt for.
        """
        return {
            "required": ["api_key"] if not self.config.api_key else [],
            "optional": ["base_url", "timeout", "rate_limit"],
            "description": self.__doc__ or "No description available",
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.config.name}', type='{self.config.connector_type.value}')>"