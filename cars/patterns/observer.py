from abc import ABC, abstractmethod
from cars.models import Notification

class Observer(ABC):
    @abstractmethod
    def update(self, message):
        pass

class UserObserver(Observer):
    def __init__(self, user):
        self.user = user
    
    def update(self, message):
        # Create a notification in DB
        Notification.objects.create(user=self.user, message=message)

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
    def change_price(self, car, new_price):
        old_price = car.price
        car.price = new_price
        car.save()
        
        # Notify all observers (followers)
        message = f"The price of {car.make} {car.model} ({car.year}) has changed from ${old_price} to ${new_price}."
        
        # Notify followers
        for follower in car.followers.all():
            Notification.objects.create(user=follower, message=message)
            
        # Also notify owner if price dropped significantly (optional logic)
        if new_price < old_price:
             Notification.objects.create(user=car.owner, message=f"You lowered the price of your {car.make} {car.model}.")
