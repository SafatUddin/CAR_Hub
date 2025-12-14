from abc import ABC, abstractmethod
from cars.models import Notification

# Observer
class Observer(ABC):
    @abstractmethod
    def update(self, message):
        pass

# Concrete Observer
class UserObserver(Observer):
    def __init__(self, user):
        self.user = user
    
    def update(self, message):
        # Create a notification in DB
        Notification.objects.create(user=self.user, message=message)

# Subject
class Subject(ABC):
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
        
    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
        
    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class CarPriceSubject(Subject):
    def __init__(self, car):
        super().__init__()
        self.car = car
        
    def change_price(self, new_price):
        # Capture old price BEFORE saving
        old_price = self.car.price
        
        # Update and save the new price
        self.car.price = new_price
        self.car.save()
        
        # Notify all observers through the proper Observer pattern mechanism
        message = f"The price of {self.car.make} {self.car.model} ({self.car.year}) has changed from ৳{old_price:.0f} to ৳{new_price:.0f}."
        self.notify(message)
