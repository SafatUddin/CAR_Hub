# CAR Hub

A car selling website built with Django and MySQL, implimenting 7 software design patterns made for Software Engineering Course(CSE327) under Supervisor AKM Iqtidar Newaz(IQN).

## Setup

1.  Install dependencies:
    ```bash
    pip install django mysqlclient
    ```
2.  Configure Database:
    *   The project is configured to use SQLite by default for development ease.
    *   To use MySQL, ensure you have a database named `car_hub_db` and set the `USE_MYSQL=True` environment variable, or edit `car_hub/settings.py`.
3.  Run Migrations:
    ```bash
    python manage.py migrate
    ```
4.  Create Superuser (Admin):
    ```bash
    python manage.py createsuperuser
    ```
5.  Run Server:
    ```bash
    python manage.py runserver
    ```
6. Superuser/Admin creation
    ```bash
    python3 manage.py createsuperuser
    ```
***

## Quick Start (How to Run the Project)

To start the project, follow these simple steps:

1. **Navigate to the project directory:**
   ```bash
   cd /home/safat/VS_Code/CAR_Hub
   ```

2. **Start the development server:**
   ```bash
   python3 manage.py runserver
   ```

3. **Access the application:**
   - Open your browser and go to: `http://127.0.0.1:8000/`
   - You'll see the welcome page if you're not logged in
   - Login or signup to access the car listings

4. **Stop the server:**
   - Press `CTRL + C` in the terminal

***

## Design Patterns Implemented

1.  **Factory Design Pattern**: Used to create different types of cars (Sedan, SUV, Truck, Coupe).
    *   Location: `cars/patterns/factory.py`
    *   Usage: `views.py` -> `create_car`
2.  **Singleton Design Pattern**: Used for Database Configuration Manager.
    *   Location: `cars/patterns/singleton.py`
    *   Usage: `views.py` -> `home`
3.  **Observer Pattern**: Used for notifications.
    *   Location: `cars/patterns/observer.py`
    *   Usage: `views.py` -> `update_price`
4.  **Strategy Design Pattern**: Used for search and filtering (Price, Brand, Mileage).
    *   Location: `cars/patterns/strategy.py`
    *   Usage: `views.py` -> `home`
5.  **Decorator Design Pattern**: Used for optional add-ons (Extended Warranty, Added Dash Cam, Custom Seat Covers, Window Tinting).
    *   Location: `cars/patterns/decorator.py`
    *   Usage: `views.py` -> `car_detail`
6.  **Proxy Design Pattern**: Used for access control (Approving car listing).
    *   Location: `cars/patterns/proxy.py`
    *   Usage: `views.py` -> `create_car`, `delete_car`
7. **Adapter Design Pattern**: Used for converting the currency in price of car and other add-ons
    *   Location: `cars/patterns/adapter.py`
    *   Usage: `views.py` -> `car_detail`


## ERD

```mermaid
erDiagram
    User ||--o{ Car : "owns"
    User ||--o{ Order : "places"
    User ||--o{ Notification : "receives"
    User ||--o| UserProfile : "has"
    User ||--o{ PurchaseRequest : "makes (as buyer)"
    User ||--o{ PurchaseRequest : "receives (as seller)"
    User }o--o{ Car : "follows"
    
    Car ||--o{ CarImage : "has"
    Car ||--o{ Order : "sold in"
    Car ||--o{ PurchaseRequest : "requested for"
    
    PurchaseRequest ||--o| Payment : "has"
    
    User {
        int id PK
        string username
        string first_name
        string email
        string password
        datetime date_joined
    }
    
    Car {
        int id PK
        string make
        string model
        int year
        decimal price
        int mileage
        string car_type
        text description
        string status
        string approval_status
        int owner_id FK
        datetime created_at
        string contact_email
        string contact_whatsapp
        file registration_paper
    }
    
    CarImage {
        int id PK
        int car_id FK
        image image
    }
    
    Order {
        int id PK
        int buyer_id FK
        int car_id FK
        string status
        datetime created_at
        bool has_warranty
        bool has_dashcam
        bool has_seatcovers
        bool has_tinting
        decimal total_price
        string payment_method
        datetime payment_completed_at
    }
    
    Notification {
        int id PK
        int user_id FK
        text message
        bool is_read
        datetime created_at
    }
    
    UserProfile {
        int id PK
        int user_id FK
        string whatsapp_number
    }
    
    PurchaseRequest {
        int id PK
        int car_id FK
        int buyer_id FK
        int seller_id FK
        string status
        text message
        datetime created_at
        datetime updated_at
    }
    
    Payment {
        int id PK
        int purchase_request_id FK
        decimal amount
        string payment_method
        string transaction_id
        string status
        datetime paid_at
        datetime created_at
        string card_last4
        string cardholder_name
    }
```

## Class Diagrams

### Django Models
```mermaid
classDiagram
    class User {
        +id int
        +username string
        +first_name string
        +email string
        +password string
    }
    
    class Car {
        +id int
        +make string
        +model string
        +year int
        +price decimal
        +mileage int
        +car_type string
        +status string
        +approval_status string
        +owner User
    }
    
    class Order {
        +id int
        +buyer User
        +car Car
        +status string
        +has_warranty bool
        +has_dashcam bool
        +has_seatcovers bool
        +has_tinting bool
        +total_price decimal
    }
    
    class Notification {
        +id int
        +user User
        +message text
        +is_read bool
    }
    
    class UserProfile {
        +id int
        +user User
        +whatsapp_number string
    }
    
    class PurchaseRequest {
        +id int
        +car Car
        +buyer User
        +seller User
        +status string
    }
    
    class Payment {
        +id int
        +purchase_request PurchaseRequest
        +amount decimal
        +transaction_id string
        +status string
    }
    
    User "1" --> "*" Car : owns
    User "1" --> "*" Order : places
    User "1" --> "*" Notification : receives
    User "1" --> "1" UserProfile : has
    Car "1" --> "*" Order : sold_in
    PurchaseRequest "1" --> "1" Payment : has
```

### Factory Pattern
```mermaid
classDiagram
    class CarFactory {
        <<abstract>>
        +create_car(make, model, year, price, mileage, owner)* Car
    }
    
    class SedanFactory {
        +create_car() Car
    }
    
    class SUVFactory {
        +create_car() Car
    }
    
    class TruckFactory {
        +create_car() Car
    }
    
    class CoupeFactory {
        +create_car() Car
    }
    
    CarFactory <|-- SedanFactory
    CarFactory <|-- SUVFactory
    CarFactory <|-- TruckFactory
    CarFactory <|-- CoupeFactory
```

### Singleton Pattern
```mermaid
classDiagram
    class DatabaseConfigManager {
        -_instance DatabaseConfigManager
        -db_connection_string string
        -max_connections int
        -pool_size int
        -timeout int
        +getInstance()$ DatabaseConfigManager
        +get_config() dict
    }
```

### Strategy Pattern
```mermaid
classDiagram
    class SearchStrategy {
        <<abstract>>
        +search(query)* QuerySet
    }
    
    class PriceSearchStrategy {
        +search(price_range) QuerySet
    }
    
    class BrandSearchStrategy {
        +search(brand_name) QuerySet
    }
    
    class MileageSearchStrategy {
        +search(mileage_range) QuerySet
    }
    
    class TypeSearchStrategy {
        +search(car_type) QuerySet
    }
    
    class YearSearchStrategy {
        +search(year_range) QuerySet
    }
    
    class CarSearchContext {
        -strategy SearchStrategy
        +set_strategy(strategy)
        +execute_search(query) QuerySet
    }
    
    SearchStrategy <|-- PriceSearchStrategy
    SearchStrategy <|-- BrandSearchStrategy
    SearchStrategy <|-- MileageSearchStrategy
    SearchStrategy <|-- TypeSearchStrategy
    SearchStrategy <|-- YearSearchStrategy
    CarSearchContext --> SearchStrategy
```

### Decorator Pattern
```mermaid
classDiagram
    class CarComponent {
        <<abstract>>
        +get_price()* float
        +get_description()* string
    }
    
    class BasicCar {
        -car Car
        +get_price() float
        +get_description() string
    }
    
    class CarDecorator {
        <<abstract>>
        -car_component CarComponent
        +get_price()* float
        +get_description()* string
    }
    
    class WarrantyDecorator {
        +get_price() float
        +get_description() string
    }
    
    class DashCamDecorator {
        +get_price() float
        +get_description() string
    }
    
    class SeatCoversDecorator {
        +get_price() float
        +get_description() string
    }
    
    class TintingDecorator {
        +get_price() float
        +get_description() string
    }
    
    CarComponent <|-- BasicCar
    CarComponent <|-- CarDecorator
    CarDecorator <|-- WarrantyDecorator
    CarDecorator <|-- DashCamDecorator
    CarDecorator <|-- SeatCoversDecorator
    CarDecorator <|-- TintingDecorator
    CarDecorator --> CarComponent
```

### Observer Pattern
```mermaid
classDiagram
    class Observer {
        <<abstract>>
        +update(message)*
    }
    
    class UserObserver {
        -user User
        +update(message)
    }
    
    class Subject {
        <<abstract>>
        -_observers List~Observer~
        +attach(observer)
        +detach(observer)
        +notify(message)
    }
    
    class CarPriceSubject {
        -car Car
        +change_price(new_price)
    }
    
    Observer <|-- UserObserver
    Subject <|-- CarPriceSubject
    Subject --> Observer
```

### Proxy Pattern
```mermaid
classDiagram
    class CarAccessInterface {
        <<abstract>>
        +delete_car(car_id)*
        +post_car(car_data)*
        +approve_car(car_id)*
        +reject_car(car_id, reason)*
    }
    
    class RealCarService {
        +delete_car(car_id)
        +post_car(car_data)
        +approve_car(car_id)
        +reject_car(car_id, reason)
    }
    
    class CarAccessProxy {
        -real_service RealCarService
        -user User
        +delete_car(car_id)
        +post_car(car_data)
        +approve_car(car_id)
        +reject_car(car_id, reason)
    }
    
    CarAccessInterface <|-- RealCarService
    CarAccessInterface <|-- CarAccessProxy
    CarAccessProxy --> RealCarService
```

### Adapter Pattern
```mermaid
classDiagram
    class CurrencyConverter {
        <<interface>>
        +convert_to_bdt(amount, currency)* float
        +convert_from_bdt(amount_bdt, target_currency)* float
        +get_currency_symbol(currency)* string
    }
    
    class ThirdPartyCurrencyAPI {
        +EXCHANGE_RATES dict
        +CURRENCY_SYMBOLS dict
        +calculate_bdt_value(amount, currency) float
        +calculate_foreign_value(amount_bdt, currency) float
        +get_symbol(currency) string
    }
    
    class CurrencyAdapter {
        -api ThirdPartyCurrencyAPI
        +convert_to_bdt(amount, currency) float
        +convert_from_bdt(amount_bdt, target_currency) float
        +get_currency_symbol(currency) string
    }
    
    CurrencyConverter <|-- CurrencyAdapter
    CurrencyAdapter --> ThirdPartyCurrencyAPI
```

## Sequence Diagram

### Car Purchase Flow
```mermaid
sequenceDiagram
    actor Buyer
    participant View as Views
    participant Decorator as Decorator Pattern
    participant Adapter as Adapter Pattern
    participant Car as Car Model
    participant Order as Order Model
    participant Observer as Observer Pattern
    participant Notification as Notification Model
    actor Seller

    Buyer->>View: GET /car/{id}/
    View->>Car: Get car details
    Car-->>View: Car object
    View->>Decorator: BasicCar(car)
    View->>Decorator: Add selected features
    Decorator-->>View: Decorated car with price
    View->>Adapter: Convert price to BDT
    Adapter-->>View: Converted price
    View-->>Buyer: Display car detail page
    
    Buyer->>View: POST /buy/{id}/ (with optional features)
    View->>Car: Check if car is available
    Car-->>View: Car available
    View->>View: Calculate total price (base + features)
    View->>Order: Create order with features
    Order-->>View: Order created
    View->>Car: Update status to 'sold'
    Car-->>View: Status updated
    
    View->>Observer: CarPriceSubject.notify()
    Observer->>Notification: Create notification for seller
    Notification-->>Observer: Notification created
    Observer-->>Seller: Notify about sale
    
    View-->>Buyer: Redirect to success page
```

### Car Listing Creation Flow
```mermaid
sequenceDiagram
    actor Seller
    participant View as Views
    participant Factory as Factory Pattern
    participant Proxy as Proxy Pattern
    participant Car as Car Model
    participant Observer as Observer Pattern
    participant Notification as Notification Model
    actor Admin

    Seller->>View: POST /create/ (car data)
    View->>View: Validate form data
    View->>Factory: Select factory (Sedan/SUV/Truck/Coupe)
    Factory->>Car: create_car()
    Car-->>Factory: Car object (status: pending)
    Factory-->>View: Car created
    View->>Proxy: CarAccessProxy.post_car()
    Proxy->>Proxy: Check user permissions
    Proxy-->>View: Car posted for approval
    View-->>Seller: Success message
    
    Admin->>View: GET /admin_dashboard/
    View->>Car: Get pending cars
    Car-->>View: List of pending cars
    View-->>Admin: Display pending listings
    
    Admin->>View: POST /approve/{id}/
    View->>Proxy: CarAccessProxy.approve_car(id)
    Proxy->>Car: Update approval_status = 'approved'
    Car-->>Proxy: Status updated
    Proxy->>Observer: Notify car owner
    Observer->>Notification: Create notification
    Notification-->>Observer: Notification created
    Observer-->>Seller: Notify about approval
    Proxy-->>View: Car approved
    View-->>Admin: Success message
```

### Price Update and Notification Flow
```mermaid
sequenceDiagram
    actor Seller
    participant View as Views
    participant Observer as Observer Pattern
    participant Car as Car Model
    participant Notification as Notification Model
    actor Follower1
    actor Follower2

    Seller->>View: POST /update_price/{id}/ (new price)
    View->>Car: Get car and verify ownership
    Car-->>View: Car object
    View->>Observer: CarPriceSubject(car)
    
    loop For each follower
        View->>Observer: Attach UserObserver(follower)
    end
    
    View->>Observer: change_price(new_price)
    Observer->>Car: Update price
    Car-->>Observer: Price updated
    
    Observer->>Observer: notify(message)
    
    loop For each observer
        Observer->>Notification: Create notification
        Notification-->>Observer: Notification created
    end
    
    Observer-->>Follower1: Notify price change
    Observer-->>Follower2: Notify price change
    Observer-->>View: Notifications sent
    View-->>Seller: Success message
```

### Search and Filter Flow
```mermaid
sequenceDiagram
    actor User
    participant View as Views
    participant Strategy as Strategy Pattern
    participant Car as Car Model

    User->>View: GET /home/ (with filters)
    View->>Strategy: CarSearchContext()
    
    alt Search by price
        View->>Strategy: set_strategy(PriceSearchStrategy)
        Strategy->>Car: Filter by price range
    else Search by brand
        View->>Strategy: set_strategy(BrandSearchStrategy)
        Strategy->>Car: Filter by brand
    else Search by type
        View->>Strategy: set_strategy(TypeSearchStrategy)
        Strategy->>Car: Filter by car type
    else Search by year
        View->>Strategy: set_strategy(YearSearchStrategy)
        Strategy->>Car: Filter by year range
    end
    
    Car-->>Strategy: Filtered queryset
    Strategy-->>View: Search results
    View-->>User: Display filtered cars
```