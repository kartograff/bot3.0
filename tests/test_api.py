import pytest
import json

def test_api_stats_appointments(client):
    response = client.get('/api/stats/appointments?days=7')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    # Optional: check structure
    if data:
        assert 'date' in data[0]
        assert 'count' in data[0]

def test_api_stats_services(client):
    response = client.get('/api/stats/services')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)