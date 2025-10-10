import pytest
from app import create_app  # Import your app factory
from app.extensions import db

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    # Create the app with the testing configuration
    app = create_app(config_class="app.config.TestingConfig")

    # Establish an application context
    with app.app_context():
        # Create the database and the database table(s)
        db.create_all()
        
        yield app  # The tests will run at this point

        # Remove the database session and drop all tables
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    """A test client for the app."""
    return app.test_client()