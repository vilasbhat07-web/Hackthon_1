"""Pure service smoke tests; use an isolated database fixture in CI."""
from app.services import forecast

def test_forecast_handles_insufficient_history():
    class Query:
        def order_by(self, *args): return self
        def all(self): return []
    class DB:
        def query(self, *args): return Query()
    assert forecast(DB()) is None
