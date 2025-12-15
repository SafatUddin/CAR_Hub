from abc import ABC, abstractmethod

# Component Interface
class CarComponent(ABC):
    @abstractmethod
    def get_price(self):
        pass
    
    @abstractmethod
    def get_description(self):
        pass

# Concrete Component
class BasicCar(CarComponent):
    def __init__(self, car_model):
        self.car = car_model
    
    def get_price(self):
        return float(self.car.price)
    
    def get_description(self):
        return f"{self.car.year} {self.car.make} {self.car.model}"

# Decorator
class CarDecorator(CarComponent):
    def __init__(self, car_component: CarComponent):
        self.car_component = car_component
    
    @abstractmethod
    def get_price(self):
        pass
    
    @abstractmethod
    def get_description(self):
        pass

# Concrete Decorators
class WarrantyDecorator(CarDecorator):
    def get_price(self):
        return self.car_component.get_price() + 50000.00
    
    def get_description(self):
        return self.car_component.get_description() + " + Extended Warranty"

class DashCamDecorator(CarDecorator):
    def get_price(self):
        return self.car_component.get_price() + 15000.00
    
    def get_description(self):
        return self.car_component.get_description() + " + Dash Cam"

class SeatCoversDecorator(CarDecorator):
    def get_price(self):
        return self.car_component.get_price() + 20000.00
    
    def get_description(self):
        return self.car_component.get_description() + " + Custom Seat Covers"

class WindowTintingDecorator(CarDecorator):
    def get_price(self):
        return self.car_component.get_price() + 10000.00
    
    def get_description(self):
        return self.car_component.get_description() + " + Window Tinting"
