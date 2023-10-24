# Python Healthcheck Lib

This is an opinionated library to help with structuring healthchecks in your python application.

It will not help you with the healthcheck logic itself, but it will help you build the response in a standard format.

We aim at supporting almost exactly the standard described in https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check. Although it's just a expired draft, it seems to be the better standard on healthchecks out there as of this writing.

This standard is not fully supported yet, see the [roadmap](#roadmap) for more information.

## Installation

```bash
# With pip
pip install python-healthchecklib

# With poetry
poetry add python-healthchecklib
```

## Concepts

The main concepts to keep in mind when using this library are the `service` and `components` concepts.

We consider a `service` to be the application as a whole. It's the thing that is running and that you want to check the health of.

We consider `components` to be the different parts of the application that you want to check the health of, being them internal or external. For example, if you have a web application, you might want to check the health of the database, the cache, internal components, etc.

You'll be responsible for implementing the healthcheck logic for each component, but this library will help you build the response in a standard format and define the health of the `service` based on the health of its `components`.

## Usage

The lib exposes asynchronous methods, which makes it easy to use with either sync or async codebases.

```python
from healthcheck import Healthcheck, HealthcheckDatastoreComponent, HealthcheckCallbackResponse

# Create a healthcheck instance
healthcheck = Healthcheck(
    name="My Service"
)

# Create a component
db_component = HealthcheckDatastoreComponent(
    name="MySQL",
)

# Define the healthcheck logic for the component.
# They should be async functions that return a HealthcheckCallbackResponse
async def db_healthcheck():
    # Implement some logic to check the health of the database
    return HealthcheckCallbackResponse(
        status="pass",
        output="Database is healthy",
        affects_service_health=True
    )

# Add the healthcheck logic to the component
db_component.add_healthcheck(db_healthcheck)

# You can add more than one healthcheck to a component, which means that this is a component made of multiple instances.
async def db_healthcheck_2():
    # Implement some logic to check the health of the database
    return HealthcheckCallbackResponse(
        status="warn",
        output="Responsive but high latency",
        affects_service_health=False
    )

db_component.add_healthcheck(db_healthcheck_2)

# Add the component to the healthcheck
healthcheck.add_component(db_component)

# Get the health status of the service
status = await healthcheck.run()

# In case you're in a sync context, you can use `asyncio.run` to run the async code:
status = asyncio.run(healthcheck.run())

# Print the status
print(status)

# {
#   "status": "pass",
#   "description": "Health status of My Service",
#   "checks": {
#     "database": [
#       {
#         "status": "pass",
#         "output": "Database is healthy",
#         "componentType": "datastore"
#       },
#       {
#         "status": "warn",
#         "output": "Responsive but high latency",
#         "componentType": "datastore"
#       }
#     ]
#   }
# }
```

## Roadmap

- [ ] Support for manually setting the component health status (instead of passing a callback)
- [ ] Support for the optional fields in the service status described in https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check#name-status
- [ ] Support for the optional fields in the component staus described in https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check#name-the-checks-object
- [ ] Support for defining customized keys for the component status object

We welcome contributions to help us achieve these goals. See below how to contribute.

## Contributing

See the [contributing guide](CONTRIBUTING.md) for more information.

## License

By contributing to python-healthchecklib, you agree that your contributions will be licensed under the [MIT License](https://opensource.org/licenses/MIT).