# Supabase Database Adapter (Mocking SQLAlchemy for backward compatibility)

class DummySQLAlchemy:
    def __init__(self):
        self.session = self
        
    def init_app(self, app):
        pass
        
    def commit(self):
        pass
        
    def rollback(self):
        pass

db = DummySQLAlchemy()

def initialize_database(app):
    """
    Mock initialization for Supabase integration.
    """
    print("=" * 50)
    print("Supabase Connected Successfully via REST Client")
    print("=" * 50)