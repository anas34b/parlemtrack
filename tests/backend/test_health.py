"""Tests du endpoint de santé."""


def test_health_ok(client) -> None:
    reponse = client.get("/api/health")

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["statut"] == "ok"
    assert corps["base_de_donnees"] is True
    assert corps["redis"] is True


def test_health_expose_les_headers_de_securite(client) -> None:
    reponse = client.get("/api/health")

    assert reponse.headers["x-content-type-options"] == "nosniff"
    assert reponse.headers["x-frame-options"] == "DENY"
