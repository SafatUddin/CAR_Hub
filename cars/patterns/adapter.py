# target interface
class CurrencyConverter:

    def convert_to_bdt(self, amount, currency): #to be implemented by adapter
        """Convert any currency to BDT"""
        raise NotImplementedError #make sure derived class implements this method
    
    def convert_from_bdt(self, amount_bdt, target_currency): #to be implemented by adapter
        """Convert BDT to any currency"""
        raise NotImplementedError #make sure derived class implements this method
    
    def get_currency_symbol(self, currency): #to be implemented by adapter
        """Get the symbol for a currency"""
        raise NotImplementedError #make sure derived class implements this method


# Adaptee - Third-party service with incompatible interface
class ThirdPartyCurrencyAPI:

    
    # Exchange rates: 1 unit of currency = X BDT
    EXCHANGE_RATES = {
        'BDT': 1.0,
        'USD': 120.0,   # 1 USD = 120 BDT
        'GBP': 150.0,   # 1 GBP = 150 BDT
        'EUR': 130.0,   # 1 EUR = 130 BDT
        'INR': 1.45     # 1 INR = 1.45 BDT
    }
    
    CURRENCY_SYMBOLS = {
        'BDT': '৳',
        'USD': '$',
        'GBP': '£',
        'EUR': '€',
        'INR': '₹'
    }
    
    def get_exchange_rate(self, currency_code):
        """Third-party API method to get exchange rate"""
        return self.EXCHANGE_RATES.get(currency_code, 1.0)
    
    def get_symbol_for_currency(self, currency_code):
        """Third-party API method to get currency symbol"""
        return self.CURRENCY_SYMBOLS.get(currency_code, '৳')
    
    def multiply_by_rate(self, amount, rate):
        """Third-party API helper method"""
        return float(amount) * rate
    
    def divide_by_rate(self, amount, rate):
        """Third-party API helper method"""
        return float(amount) / rate


# Adapter - Makes the adaptee compatible with the target interface
class CurrencyAdapter(CurrencyConverter):
    
    def __init__(self):
        # Composition: Adapter contains an instance of the adaptee
        self._api = ThirdPartyCurrencyAPI()
    
    def convert_to_bdt(self, amount, currency):
        rate = self._api.get_exchange_rate(currency)
        return self._api.multiply_by_rate(amount, rate)
    
    def convert_from_bdt(self, amount_bdt, target_currency):
        rate = self._api.get_exchange_rate(target_currency)
        return self._api.divide_by_rate(amount_bdt, rate)
    
    def get_currency_symbol(self, currency):
        return self._api.get_symbol_for_currency(currency)
    
    # Convenience class methods for backward compatibility
    @classmethod
    def convert_to_bdt_static(cls, amount, from_currency):
        """Static helper method for quick conversions"""
        adapter = cls()
        return adapter.convert_to_bdt(amount, from_currency)
    
    @classmethod
    def get_symbol(cls, currency):
        """Static helper method to get currency symbol"""
        adapter = cls()
        return adapter.get_currency_symbol(currency)
