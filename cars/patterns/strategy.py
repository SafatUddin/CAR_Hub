from abc import ABC, abstractmethod
from cars.models import Car

class SearchStrategy(ABC):
    @abstractmethod
    def search(self, query):
        pass

class PriceSearchStrategy(SearchStrategy):
    def search(self, price_range):
        # price_range is expected to be a tuple or list: [min_price, max_price]
        min_price, max_price = price_range
        return Car.objects.filter(price__gte=min_price, price__lte=max_price)

class BrandSearchStrategy(SearchStrategy):
    def search(self, brand_name):
        return Car.objects.filter(make__icontains=brand_name)

class ModelSearchStrategy(SearchStrategy):
    def search(self, model_name):
        return Car.objects.filter(model__icontains=model_name)

class MileageSearchStrategy(SearchStrategy):
    def search(self, mileage_range):
        # mileage_range is expected to be a tuple or list: [min_mileage, max_mileage]
        min_mileage, max_mileage = mileage_range
        return Car.objects.filter(mileage__gte=min_mileage, mileage__lte=max_mileage)

class TypeSearchStrategy(SearchStrategy):
    def search(self, car_type):
        return Car.objects.filter(car_type__iexact=car_type)

class YearSearchStrategy(SearchStrategy):
    def search(self, year_range):
        # year_range is expected to be a tuple or list: [min_year, max_year]
        min_year, max_year = year_range
        return Car.objects.filter(year__gte=min_year, year__lte=max_year)

class CarSearchContext:
    def __init__(self, strategy: SearchStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: SearchStrategy):
        self.strategy = strategy
    
    def execute_search(self, query):
        return self.strategy.search(query)
