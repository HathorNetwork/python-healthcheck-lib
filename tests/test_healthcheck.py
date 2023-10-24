# test_healthcheck.py

import unittest
from unittest.mock import ANY

from healthcheck import (
    Healthcheck,
    HealthcheckCallbackResponse,
    HealthcheckDatastoreComponent,
    HealthcheckStatus,
)


class TestHealthcheck(unittest.IsolatedAsyncioTestCase):
    async def test_base_success_case(self) -> None:
        # Create a healthcheck instance
        healthcheck = Healthcheck(name="My Service")

        # Create a component
        db_component = HealthcheckDatastoreComponent(
            name="MySQL",
        )

        # Define the healthcheck logic for the component
        async def db_healthcheck() -> HealthcheckCallbackResponse:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.PASS,
                output="Database is healthy",
                affects_service_health=True,
            )

        # Add the healthcheck logic to the component
        db_component.add_healthcheck(db_healthcheck)

        healthcheck.add_component(db_component)

        status = await healthcheck.run()

        self.assertEqual(
            status.to_json(),
            {
                "status": "pass",
                "description": "Health status of My Service",
                "checks": {
                    "MySQL": [
                        {
                            "status": "pass",
                            "output": "Database is healthy",
                            "componentName": "MySQL",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ]
                },
            },
        )
        self.assertEqual(status.get_http_status_code(), 200)

    async def test_affects_service_health_false(self) -> None:
        # Create a healthcheck instance
        healthcheck = Healthcheck(name="My Service")

        # Create a component
        db_component = HealthcheckDatastoreComponent(
            name="MySQL",
        )

        # Define the healthcheck logic for the component
        async def db_healthcheck() -> HealthcheckCallbackResponse:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.PASS,
                output="Database is healthy",
                affects_service_health=True,
            )

        # Add the healthcheck logic to the component
        db_component.add_healthcheck(db_healthcheck)

        # Add another healthcheck to the component
        async def db_healthcheck_2() -> HealthcheckCallbackResponse:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.FAIL,
                output="Unresponsive database",
                affects_service_health=False,
            )

        db_component.add_healthcheck(db_healthcheck_2)

        healthcheck.add_component(db_component)

        status = await healthcheck.run()

        self.assertEqual(
            status.to_json(),
            {
                "status": "pass",
                "description": "Health status of My Service",
                "checks": {
                    "MySQL": [
                        {
                            "status": "pass",
                            "output": "Database is healthy",
                            "componentName": "MySQL",
                            "componentType": "datastore",
                            "time": ANY,
                        },
                        {
                            "status": "fail",
                            "output": "Unresponsive database",
                            "componentName": "MySQL",
                            "componentType": "datastore",
                            "time": ANY,
                        },
                    ]
                },
            },
        )
        self.assertEqual(status.get_http_status_code(), 200)

    async def test_affects_service_health_true(self) -> None:
        # Create a healthcheck instance
        healthcheck = Healthcheck(name="My Service")

        # Create a component
        db_component = HealthcheckDatastoreComponent(
            name="MySQL",
        )

        # Define the healthcheck logic for the component
        async def db_healthcheck() -> HealthcheckCallbackResponse:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.PASS,
                output="Database is healthy",
                affects_service_health=True,
            )

        # Add the healthcheck logic to the component
        db_component.add_healthcheck(db_healthcheck)

        # Add another healthcheck to the component
        async def db_healthcheck2() -> HealthcheckCallbackResponse:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.FAIL,
                output="Unresponsive database",
                affects_service_health=True,
            )

        db_component.add_healthcheck(db_healthcheck2)

        healthcheck.add_component(db_component)

        status = await healthcheck.run()

        self.assertEqual(
            status.to_json(),
            {
                "status": "fail",
                "description": "Health status of My Service",
                "checks": {
                    "MySQL": [
                        {
                            "status": "pass",
                            "output": "Database is healthy",
                            "componentName": "MySQL",
                            "componentType": "datastore",
                            "time": ANY,
                        },
                        {
                            "status": "fail",
                            "output": "Unresponsive database",
                            "componentName": "MySQL",
                            "componentType": "datastore",
                            "time": ANY,
                        },
                    ]
                },
            },
        )
        self.assertEqual(status.get_http_status_code(), 503)

    async def test_warn_is_unhealthy(self) -> None:
        # Create a healthcheck instance
        healthcheck = Healthcheck(name="My Service", warn_is_unhealthy=True)

        # Create a component
        db_component = HealthcheckDatastoreComponent(
            name="MySQL",
        )

        # Define the healthcheck logic for the component
        async def db_healthcheck() -> HealthcheckCallbackResponse:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.PASS,
                output="Database is healthy",
                affects_service_health=True,
            )

        # Add the healthcheck logic to the component
        db_component.add_healthcheck(db_healthcheck)

        # Add another healthcheck to the component
        async def db_healthcheck2() -> HealthcheckCallbackResponse:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.WARN,
                output="Responsive but high latency",
                affects_service_health=True,
            )

        db_component.add_healthcheck(db_healthcheck2)

        healthcheck.add_component(db_component)

        status = await healthcheck.run()

        self.assertEqual(
            status.to_json(),
            {
                "status": "warn",
                "description": "Health status of My Service",
                "checks": {
                    "MySQL": [
                        {
                            "status": "pass",
                            "output": "Database is healthy",
                            "componentName": "MySQL",
                            "componentType": "datastore",
                            "time": ANY,
                        },
                        {
                            "status": "warn",
                            "output": "Responsive but high latency",
                            "componentName": "MySQL",
                            "componentType": "datastore",
                            "time": ANY,
                        },
                    ]
                },
            },
        )

        self.assertEqual(status.get_http_status_code(), 503)
