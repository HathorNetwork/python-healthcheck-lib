from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from healthcheck.utils import get_enum_value


class ComponentType(str, Enum):
    """Enum used to store the component types."""

    DATASTORE = "datastore"
    INTERNAL = "internal"
    HTTP = "http"
    GENERIC = "generic"


class HealthcheckStatus(str, Enum):
    """Enum used to store the possible service and component health status."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class HealthcheckCallbackResponse:
    """This class is used to store the result of a health check callback."""

    status: HealthcheckStatus
    output: str
    affects_service_health: bool = True


@dataclass
class HealthcheckComponentStatus:
    """This class is used to store the result of a health check in a specific component."""

    component_name: str
    component_type: ComponentType
    status: HealthcheckStatus
    output: str
    time: Optional[datetime] = None
    component_id: Optional[str] = None
    observed_value: Optional[str] = None
    observed_unit: Optional[str] = None
    _affects_service_health: Optional[bool] = True

    def __post_init__(self) -> None:
        self.time = datetime.utcnow()

    def to_json(self) -> Dict[str, str]:
        """Return a dict representation of the object. All field names are converted to camel case."""
        json = {
            "componentName": self.component_name,
            "componentType": get_enum_value(self.component_type),
            "status": get_enum_value(self.status),
            "output": self.output,
        }

        if self.time:
            json["time"] = self.time.strftime("%Y-%m-%dT%H:%M:%SZ")

        if self.component_id:
            json["componentId"] = self.component_id

        if self.observed_value:
            assert self.observed_unit is not None, "observed_unit must be set if observed_value is set"

            json["observedValue"] = self.observed_value
            json["observedUnit"] = self.observed_unit

        return json


@dataclass
class HealthcheckResponse:
    """Represents the final result of a healthcheck in a service."""

    status: HealthcheckStatus
    description: str
    checks: Dict[str, List[HealthcheckComponentStatus]]
    _http_status_code: Optional[int] = None

    def get_http_status_code(self) -> int:
        assert self._http_status_code is not None, "http_status_code must be set"

        return self._http_status_code

    def filter_checks_by_status(self, status: HealthcheckStatus) -> Dict[str, List[HealthcheckComponentStatus]]:
        """Return a dict of checks that have the given status."""
        return {k: v for k, v in self.checks.items() if any(c.status == status for c in v)}

    def to_json(self) -> Dict[str, Any]:
        """Return a dict representation of the object. All field names are converted to camel case."""
        return {
            "status": get_enum_value(self.status),
            "description": self.description,
            "checks": {k: [c.to_json() for c in v] for k, v in self.checks.items()},
        }
