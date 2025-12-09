class DatabaseConfigManager:
    
    # Private static instance variable
    _instance = None
    
    def __new__(cls):
        """
        Private constructor - controls object creation.
        Only creates a new instance if one doesn't exist.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConfigManager, cls).__new__(cls)
            # Initialize configuration only once
            cls._instance._initialize_config()
        return cls._instance
    
    def _initialize_config(self):
        """
        Private method to initialize configuration.
        Called only once when the instance is first created.
        """
        self.db_connection_string = "mysql://root:password@localhost:3306/car_hub_db"
        self.max_connections = 100
        self.pool_size = 10
        self.timeout = 30
    
    @classmethod
    def getInstance(cls):
        """
        Public static method to get the singleton instance.
        This is the standard way to access the singleton.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_connection_string(self):
        """Get the database connection string"""
        return self.db_connection_string
    
    def get_config(self):
        """
        Get the complete database configuration.
        """
        return {
            "connection": self.db_connection_string,
            "max_connections": self.max_connections,
            "pool_size": self.pool_size,
            "timeout": self.timeout
        }
    
    def update_max_connections(self, new_max):
        """Update maximum connections (affects all references)"""
        self.max_connections = new_max
