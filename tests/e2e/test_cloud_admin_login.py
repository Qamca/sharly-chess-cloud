"""E2E tests for CLOUD_MODE global admin authentication."""

import pytest
from argon2 import PasswordHasher
from playwright.sync_api import Page, expect

from database.sqlite.event.event_database import EventDatabase
from database.sqlite.event.event_store import StoredAccount, StoredEvent
from data.board import PlayerRatingType
from tests.test_config import TestConfig


_CLOUD_EVENT_ID = 'cloud-per-event-test'
_PER_EVENT_PASSWORD = 'per-event-test-password'


@pytest.fixture(scope='module')
def cloud_event(cloud_backend_server):
    """Creates a test event with one account directly in the cloud data directory."""
    if not cloud_backend_server:
        pytest.skip('Cloud backend server not available')

    events_dir = TestConfig.CLOUD_TEST_DATA_DIR.resolve() / 'events'
    events_dir.mkdir(parents=True, exist_ok=True)
    event_file = events_dir / f'{_CLOUD_EVENT_ID}.sce'
    event_file.unlink(missing_ok=True)

    database = EventDatabase(file_path=event_file)
    database.create()

    stored_event = StoredEvent(
        uniq_id=_CLOUD_EVENT_ID,
        name=_CLOUD_EVENT_ID,
        federation='FRA',
        player_rating_type=PlayerRatingType.FIDE.value,
        public=True,
    )
    with EventDatabase(file_path=event_file, write=True) as db:
        db.update_stored_event(stored_event)

    ph = PasswordHasher()
    stored_account = StoredAccount(
        id=None,
        active=True,
        first_name='Cloud',
        last_name='Tester',
        password_hash=ph.hash(_PER_EVENT_PASSWORD),
    )
    with EventDatabase(file_path=event_file, write=True) as db:
        db.add_stored_account(stored_account)

    yield _CLOUD_EVENT_ID, _PER_EVENT_PASSWORD

    event_file.unlink(missing_ok=True)


@pytest.mark.e2e
class TestCloudAdminAuth:
    def test_cloud_admin_login_success(self, cloud_page: Page):
        """Correct password grants admin access and shows the create-event button."""
        cloud_page.goto('/')
        cloud_page.wait_for_load_state('domcontentloaded')

        cloud_page.get_by_test_id('cloud-admin-button').click()
        cloud_page.wait_for_selector('.modal-dialog', state='visible')

        cloud_page.locator('#password').fill(TestConfig.CLOUD_ADMIN_PASSWORD)
        cloud_page.locator('#modal-form button[type=submit]').click()

        # After redirect, the create-event button must be visible (admin-only control)
        expect(cloud_page.get_by_role('button', name='Create an event')).to_be_visible()
        # The cloud admin button should now display the authenticated icon
        expect(
            cloud_page.get_by_test_id('cloud-admin-button').locator('.bi-person-fill-check')
        ).to_be_visible()

    def test_cloud_admin_login_wrong_password(self, cloud_page: Page):
        """Wrong password shows an error and does not grant admin access."""
        cloud_page.goto('/')
        cloud_page.get_by_test_id('cloud-admin-button').click()
        cloud_page.wait_for_selector('.modal-dialog', state='visible')

        cloud_page.locator('#password').fill('wrong-password')
        cloud_page.locator('#modal-form button[type=submit]').click()

        # Error feedback and "Not logged in" heading must appear; the modal stays open
        expect(cloud_page.locator('.modal-dialog .invalid-feedback')).to_be_visible()
        expect(
            cloud_page.locator('.modal-dialog h4').filter(has_text='Not logged in')
        ).to_be_visible()

    def test_cloud_admin_logout(self, cloud_page: Page):
        """Admin can log out after a successful login."""
        cloud_page.goto('/')

        # Log in first
        cloud_page.get_by_test_id('cloud-admin-button').click()
        cloud_page.wait_for_selector('.modal-dialog', state='visible')
        cloud_page.locator('#password').fill(TestConfig.CLOUD_ADMIN_PASSWORD)
        cloud_page.locator('#modal-form button[type=submit]').click()
        expect(cloud_page.get_by_role('button', name='Create an event')).to_be_visible()

        # Open the modal again and log out
        cloud_page.get_by_test_id('cloud-admin-button').click()
        cloud_page.wait_for_selector('.modal-dialog', state='visible')
        cloud_page.locator('#modal-form button[type=submit]').click()

        # Admin controls must be gone; lock icon back
        expect(cloud_page.get_by_role('button', name='Create an event')).not_to_be_visible()
        expect(
            cloud_page.get_by_test_id('cloud-admin-button').locator('.bi-person-lock')
        ).to_be_visible()

    def test_per_event_login_unaffected(self, cloud_page: Page, cloud_event):
        """Per-event account login still works normally when CLOUD_MODE is enabled."""
        event_id, password = cloud_event

        cloud_page.goto(f'/event/{event_id}')
        cloud_page.wait_for_load_state('domcontentloaded')

        cloud_page.get_by_test_id('profile-button').click()
        cloud_page.wait_for_selector('.modal-dialog', state='visible')
        cloud_page.locator('#password').fill(password)
        cloud_page.locator('#modal-form button[type=submit]').click()

        # Per-event login should display the account full name in the sidebar button
        expect(cloud_page.get_by_test_id('profile-button')).to_contain_text('Cloud Tester')
