"""Unit tests for the CLOUD_MODE authentication logic in Client._get_account()."""

from unittest.mock import MagicMock

import pytest

import data.access_levels.client as client_module
from data.access_levels.client import Client
from data.account import Account


def _make_request(host: str, session: dict | None = None) -> MagicMock:
    """Build a minimal mock HTMXRequest with the given client host and session."""
    request = MagicMock()
    request.client.host = host
    request.session = session or {}
    return request


@pytest.mark.unit
class TestCloudModeAuth:
    def test_localhost_bypass_active_without_cloud_mode(self, monkeypatch):
        """When CLOUD_MODE is off, localhost gets admin account automatically."""
        monkeypatch.setattr(client_module, 'CLOUD_MODE', False)
        request = _make_request('127.0.0.1')
        client = Client.__new__(Client)
        client.request = request
        client.host = '127.0.0.1'
        client.event = None
        account = client._get_account()
        assert account.administrator, 'Localhost should have admin access when CLOUD_MODE is off'

    def test_localhost_bypass_disabled_in_cloud_mode(self, monkeypatch):
        """When CLOUD_MODE is on, localhost no longer auto-gets admin access."""
        monkeypatch.setattr(client_module, 'CLOUD_MODE', True)
        request = _make_request('127.0.0.1')
        client = Client.__new__(Client)
        client.request = request
        client.host = '127.0.0.1'
        client.event = None
        account = client._get_account()
        assert account.anonymous, 'Localhost should NOT have admin access when CLOUD_MODE is on'

    def test_cloud_admin_session_grants_admin(self, monkeypatch):
        """When CLOUD_MODE is on and the session has cloud_admin_authenticated=True, admin is granted."""
        monkeypatch.setattr(client_module, 'CLOUD_MODE', True)
        request = _make_request('1.2.3.4', session={'cloud_admin_authenticated': True})
        client = Client.__new__(Client)
        client.request = request
        client.host = '1.2.3.4'
        client.event = None
        account = client._get_account()
        assert account.administrator, 'Cloud admin session should grant admin account'

    def test_no_session_gives_anonymous_in_cloud_mode(self, monkeypatch):
        """When CLOUD_MODE is on but no cloud admin session, non-event access is anonymous."""
        monkeypatch.setattr(client_module, 'CLOUD_MODE', True)
        request = _make_request('1.2.3.4', session={})
        client = Client.__new__(Client)
        client.request = request
        client.host = '1.2.3.4'
        client.event = None
        account = client._get_account()
        assert account.anonymous, 'Without cloud admin session, access should be anonymous'

    def test_cloud_mode_off_external_ip_no_event_is_anonymous(self, monkeypatch):
        """Sanity check: external IP without CLOUD_MODE and without event is also anonymous."""
        monkeypatch.setattr(client_module, 'CLOUD_MODE', False)
        request = _make_request('5.6.7.8', session={})
        client = Client.__new__(Client)
        client.request = request
        client.host = '5.6.7.8'
        client.event = None
        account = client._get_account()
        assert account.anonymous
