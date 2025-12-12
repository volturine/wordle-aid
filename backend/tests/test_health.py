from fastapi.testclient import TestClient


def test_healthcheck(monkeypatch, tmp_path):
    monkeypatch.setenv('DB_ROOT_PATH', str(tmp_path))

    import main

    client = TestClient(main.app)

    response = client.get('/api/health')
    assert response.status_code == 200

    payload = response.json()
    assert payload['status'] == 'ok'
    assert 'timestamp' in payload
