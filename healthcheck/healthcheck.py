import asyncio
from abc import ABC
from typing import Any, Callable, Coroutine, Optional

from healthcheck.models import (
    ComponentType,
    HealthcheckCallbackResponse,
    HealthcheckComponentStatus,
    HealthcheckResponse,
    HealthcheckStatus,
)


class HealthcheckComponentInterface(ABC):
    component_type: ComponentType

    def __init__(self, name: str, id: Optional[str] = None) -> None:
        self.name: str = name
        self.id: Optional[str] = id
        self.healthchecks: list[Callable[[], Coroutine[Any, Any, HealthcheckCallbackResponse]]] = []

    def __post_init__(self) -> None:
        assert self.component_type is not None, "component_type must be set"

    def add_healthcheck(self, coroutine: Callable[[], Coroutine[Any, Any, HealthcheckCallbackResponse]]) -> "HealthcheckComponentInterface":
        """Add a coroutine function as a healthcheck."""
        self.healthchecks.append(coroutine)

        # Return self so that we can chain calls to this method
        return self

    async def _run_async_healthchecks(self) -> list[HealthcheckCallbackResponse]:
        return await asyncio.gather(*[coroutine() for coroutine in self.healthchecks])  # type: ignore[no-any-return]

    async def run(self) -> list[HealthcheckComponentStatus]:
        results: list[HealthcheckComponentStatus] = []

        healthcheck_results = await self._run_async_healthchecks()

        for result in healthcheck_results:
            assert isinstance(result, HealthcheckCallbackResponse), "HealthcheckCallbackResponse expected"

            results.append(
                HealthcheckComponentStatus(
                    component_name=self.name,
                    component_type=self.component_type,
                    component_id=self.id,
                    status=result.status,
                    output=result.output,
                    _affects_service_health=result.affects_service_health,
                )
            )

        return results


class HealthcheckDatastoreComponent(HealthcheckComponentInterface):
    component_type = ComponentType.DATASTORE


class HealthcheckInternalComponent(HealthcheckComponentInterface):
    component_type = ComponentType.INTERNAL


class HealthcheckHTTPComponent(HealthcheckComponentInterface):
    component_type = ComponentType.HTTP


class HealthcheckGenericComponent(HealthcheckComponentInterface):
    component_type = ComponentType.GENERIC


class Healthcheck:
    def __init__(
        self,
        name: str,
        components: list[HealthcheckComponentInterface] = [],
        warn_is_unhealthy: bool = False,
    ) -> None:
        self.name = name
        self.components: list[HealthcheckComponentInterface] = components
        self.warn_is_unhealthy = warn_is_unhealthy

        self.checks: dict[str, list[HealthcheckComponentStatus]] = {}

    @property
    def status(self) -> HealthcheckStatus:
        """Return the status of the health check based on the status of the components."""
        status = HealthcheckStatus.PASS

        for component_checks in self.checks.values():
            for check in component_checks:
                if check._affects_service_health is False:
                    continue

                if check.status == HealthcheckStatus.FAIL:
                    return HealthcheckStatus.FAIL
                elif check.status == HealthcheckStatus.WARN:
                    status = HealthcheckStatus.WARN

        return status

    @property
    def description(self) -> str:
        return "Health status of " + self.name

    def add_component(self, component: HealthcheckComponentInterface) -> None:
        self.components.append(component)

    def reset_checks(self) -> None:
        self.checks = {}

    async def run(self) -> HealthcheckResponse:
        self.reset_checks()

        results = await asyncio.gather(*[component.run() for component in self.components])

        for component, result in zip(self.components, results):
            self.checks[component.name] = result

        return HealthcheckResponse(
            status=self.status,
            description=self.description,
            checks=self.checks,
            _http_status_code=self.get_http_status_code(),
        )

    def get_http_status_code(self) -> int:
        """Return a HTTP status code for the status."""
        if self.status == HealthcheckStatus.PASS:
            return 200
        if self.status == HealthcheckStatus.WARN and not self.warn_is_unhealthy:
            return 200
        if self.status == HealthcheckStatus.WARN and self.warn_is_unhealthy:
            return 503
        elif self.status == HealthcheckStatus.FAIL:
            return 503
        else:
            raise ValueError(f"Unrecognized status {self.status}")
