from backend.app.core.config import settings
import pytest

@pytest.fixture # Dependency injection
def base_url():
	return settings.DATABASE_URL

