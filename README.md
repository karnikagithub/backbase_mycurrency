# MyCurrency - Currency Exchange API

MyCurrency is a Django-based application that retrieves and stores currency exchange rates
from multiple providers using the Adapter Design Pattern. It exposes a REST API with Django
Rest Framework (DRF) and includes an admin interface.


## Features
- Retrieve exchange rates for a specific time period
- Convert an amount between currencies
- Manage currencies (Create, Read, Update, Delete)
- Provider prioritization with dynamic activation/deactivation
- Background tasks for data ingestion and updates


## Setup Instructions
### Prerequisites
- Python 3.8+
- PostgreSQL or SQLite
- Django and required dependencies


### Installation
1. Clone the repository:
```sh
git clone https://github.com/karnikagithub/backbase_mycurrency.git
cd MyCurrency
```
2. Create a virtual environment and install dependencies:
```sh
python -m venv env
source env/bin/activate # On Windows: env\Scripts\activate.bat
pip install -r requirements.txt
```
3. Set up the database:
```sh
python manage.py migrate
```
4. Load initial data (currencies and providers):
```sh
python manage.py load_initials
```
5. Run the server:
```sh
python manage.py runserver --noreload
```
## Running Tests
To run the test suite:
```sh
python manage.py test
python manage.py test currencyapp
```

## Using Postman Collection
1. Import the provided Postman collection (`postman_collection.json`) into Postman.
2. Update environment variables if needed.
3. Test the available endpoints.


## Code Structure Explanation
### `exchange_providers_adaptor.py`
Handles the integration with multiple exchange rate providers using the Adapter Pattern.
### `exchange_rate_factory.py`
Implements a Factory Pattern to dynamically create exchange rate provider instances.
### `services.py`
Contains business logic related to exchange rates, conversion, and provider prioritization.
### `tasks.py`
Manages background tasks for fetching and storing exchange rates.
### `tests/`
Includes unit and integration tests for API endpoints and services.
### `load_initials.py`
Preloads initial currency and provider data into the database.
---
© 2025 MyCurrency
