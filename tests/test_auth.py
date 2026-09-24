import importlib
import os


def test_auth_module_uses_default_secret_when_env_missing(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    import backend.auth as auth
    importlib.reload(auth)

    assert auth.SECRET_KEY
    assert auth.create_access_token({"sub": "user-1"})
