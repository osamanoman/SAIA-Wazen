"""
Database Router for SAIA Business Management System

This router ensures:
1. SAIA system models (Django built-in + our business models) use 'default' database
2. Client data source queries use 'client_data' database (read-only)
3. No migrations are run on client database
"""


class SAIADatabaseRouter:
    """
    A router to control all database operations on models for different
    databases
    """
    
    # SAIA system apps that use the default database
    saia_apps = {
        'admin',
        'auth',
        'contenttypes',
        'sessions',
        'messages',
        'staticfiles',
        'django_ai_assistant',
        'users',  # ADD: users app
        'product',
        'company',
        'invoice',
        'project',
    }
    
    # Client data source database
    client_db = 'client_data'
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        if model._meta.app_label in self.saia_apps:
            return 'default'
        return None
    
    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        if model._meta.app_label in self.saia_apps:
            return 'default'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app."""
        db_set = {'default', self.client_db}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        if app_label in self.saia_apps:
            # SAIA apps only migrate to default database
            return db == 'default'
        elif db == self.client_db:
            # Never migrate anything to client database (MySQL)
            return False
        return None
