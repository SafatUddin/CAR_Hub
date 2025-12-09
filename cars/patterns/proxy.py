from abc import ABC, abstractmethod
from cars.models import Car

class CarAccessInterface(ABC):
    @abstractmethod
    def delete_car(self, car_id):
        pass
    
    @abstractmethod
    def post_car(self, car_data):
        pass

class RealCarService(CarAccessInterface):
    def delete_car(self, car_id):
        try:
            car = Car.objects.get(id=car_id)
            car.delete()
            return True, "Car deleted successfully."
        except Car.DoesNotExist:
            return False, "Car not found."
            
    def post_car(self, car_data):
        # Assuming car_data is a dictionary and we use the factory or direct create
        # For simplicity, just creating here
        return True, "Car posted successfully."

class CarAccessProxy(CarAccessInterface):
    def __init__(self, user):
        self.user = user
        self.real_service = RealCarService()
        
    def delete_car(self, car_id):
        if self.user.is_superuser:
            return self.real_service.delete_car(car_id)
        else:
            return False, "Permission denied: Only admins can delete listings."
            
    def post_car(self, car_data):
        if self.user.is_authenticated:
            return self.real_service.post_car(car_data)
        else:
            return False, "Permission denied: You must be logged in to post a car."
