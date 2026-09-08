"""Regression tests for Ziroom air conditioner control."""

from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, call


PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "custom_components" / "ziroom"))

from ziroom_api import ZiroomApi  # noqa: E402


class TestAirconControl(unittest.TestCase):
    """Test air conditioner command sequencing and state refreshes."""

    def setUp(self) -> None:
        """Create an API client with mocked device operations."""
        self.api = ZiroomApi(token="test-token")
        self.api._set_device_prop = Mock(return_value=True)
        self.api._wait_for_state_update = Mock(return_value=True)

    def test_turn_on_and_change_mode_executes_both_commands(self) -> None:
        """Turning on with a mode must not discard the mode command."""
        result = self.api.control_aircon(
            "aircon-id",
            mode=1,
            on=True,
        )

        self.assertTrue(result)
        self.assertEqual(
            self.api._set_device_prop.call_args_list,
            [
                call("aircon-id", "set_on_off", "1"),
                call("aircon-id", "set_mode", "1"),
            ],
        )
        self.assertEqual(
            self.api._wait_for_state_update.call_args_list,
            [
                call("aircon-id", "conditioner_powerstate", "1"),
                call("aircon-id", "conditioner_model", "1"),
            ],
        )

    def test_turn_off_does_not_send_other_commands(self) -> None:
        """Turning off should stop after the power command."""
        result = self.api.control_aircon(
            "aircon-id",
            temperature=24,
            mode=1,
            speed=80,
            on=False,
        )

        self.assertTrue(result)
        self.api._set_device_prop.assert_called_once_with(
            "aircon-id",
            "set_on_off",
            "0",
        )
        self.api._wait_for_state_update.assert_called_once_with(
            "aircon-id",
            "conditioner_powerstate",
            "0",
        )

    def test_control_fails_when_state_does_not_update(self) -> None:
        """A state confirmation timeout must be visible to the caller."""
        self.api._wait_for_state_update.return_value = False

        result = self.api.control_aircon("aircon-id", on=True)

        self.assertFalse(result)

    def test_wait_for_state_update_bypasses_detail_cache(self) -> None:
        """Every state poll must request fresh device details."""
        self.api.get_device_detail = Mock(
            side_effect=[
                {"devStateMap": {"conditioner_powerstate": "0"}},
                {"devStateMap": {"conditioner_powerstate": "1"}},
            ]
        )

        result = ZiroomApi._wait_for_state_update(
            self.api,
            "aircon-id",
            "conditioner_powerstate",
            "1",
            timeout=1,
            poll_interval=0,
        )

        self.assertTrue(result)
        self.assertEqual(
            self.api.get_device_detail.call_args_list,
            [
                call("aircon-id", force_refresh=True),
                call("aircon-id", force_refresh=True),
            ],
        )


if __name__ == "__main__":
    unittest.main()
