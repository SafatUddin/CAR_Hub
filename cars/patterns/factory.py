from abc import ABC, abstractmethod

# Car -> Product
from cars.models import Car

# Concrete Products inside models.py 
#  CAR_TYPES = (
#      ('sedan', 'Sedan'),
#      ('suv', 'SUV'),
#      ('truck', 'Truck'),
#      ('coupe', 'Coupe'),
#  )

# Creator 
class CarFactory(ABC):
    @abstractmethod
    def create_car(self, make, model, year, price, mileage, owner):
        pass

# Concrete Creators
class SedanFactory(CarFactory):
    def create_car(self, make, model, year, price, mileage, owner):
        return Car.objects.create(
            make=make, model=model, year=year, price=price, 
            mileage=mileage, car_type='sedan', owner=owner
        )

class SUVFactory(CarFactory):
    def create_car(self, make, model, year, price, mileage, owner):
        return Car.objects.create(
            make=make, model=model, year=year, price=price, 
            mileage=mileage, car_type='suv', owner=owner
        )

class TruckFactory(CarFactory):
    def create_car(self, make, model, year, price, mileage, owner):
        return Car.objects.create(
            make=make, model=model, year=year, price=price, 
            mileage=mileage, car_type='truck', owner=owner
        )

class CoupeFactory(CarFactory):
    def create_car(self, make, model, year, price, mileage, owner):
        return Car.objects.create(
            make=make, model=model, year=year, price=price, 
            mileage=mileage, car_type='coupe', owner=owner
        )
