from abc import ABC, abstractmethod
from cars.models import Car

class CarAccessInterface(ABC):
    @abstractmethod
    def delete_car(self, car_id):
        pass
    
    @abstractmethod
    def post_car(self, car_data):
        pass
    
    @abstractmethod
    def approve_car(self, car_id):
        pass
    
    @abstractmethod
    def reject_car(self, car_id, reason):
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
    
    def approve_car(self, car_id):
        try:
            car = Car.objects.get(id=car_id)
            car.approval_status = 'approved'
            car.save()
            
            # Notify owner
            from cars.models import Notification
            Notification.objects.create(
                user=car.owner,
                message=f"Your listing '{car.year} {car.make} {car.model}' has been approved by admin and is now visible to buyers."
            )
            return True, "Car listing approved successfully."
        except Car.DoesNotExist:
            return False, "Car not found."
    
    def reject_car(self, car_id, reason=""):
        try:
            car = Car.objects.get(id=car_id)
            car.approval_status = 'rejected'
            car.save()
            
            # Notify owner
            from cars.models import Notification
            message = f"Your listing '{car.year} {car.make} {car.model}' has been rejected by admin."
            if reason:
                message += f" Reason: {reason}"
            Notification.objects.create(
                user=car.owner,
                message=message
            )
            return True, "Car listing rejected."
        except Car.DoesNotExist:
            return False, "Car not found."

class CarAccessProxy(CarAccessInterface):
    def __init__(self, user):
        self.user = user
        self.real_service = RealCarService()
        
    def delete_car(self, car_id):
        if self.user.is_superuser:
            return self.real_service.delete_car(car_id)
        # Allow owner to delete their own car
        try:
            car = Car.objects.get(id=car_id)
            if self.user == car.owner:
                return self.real_service.delete_car(car_id)
        except Car.DoesNotExist:
            return False, "Car not found."
        return False, "Permission denied: You are not authorized to delete this car."
            
    def post_car(self, car_data):
        if not self.user.is_authenticated:
            return False, "Permission denied: You must be logged in to post a car."
        if self.user.is_superuser:
            return False, "Permission denied: Admin users cannot list cars for sale."
        return self.real_service.post_car(car_data)
    
    def approve_car(self, car_id):
        if not self.user.is_superuser:
            return False, "Permission denied: Only admin can approve car listings."
        return self.real_service.approve_car(car_id)
    
    def reject_car(self, car_id, reason=""):
        if not self.user.is_superuser:
            return False, "Permission denied: Only admin can reject car listings."
        return self.real_service.reject_car(car_id, reason)
