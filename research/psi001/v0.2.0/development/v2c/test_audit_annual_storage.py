"""Hand-calculated and corrupt-record controls for the independent auditor."""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

from audit_annual_storage import audit_hour, digest, verify_manifest


class ArchivedTraceAuditTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "import_limit": 95, "pump_limit": 18, "boiler_limit": 100,
            "cop": 2.5, "boiler_cost": 45,
            "storage": {"capacity": 8, "charge_limit": 4, "discharge_limit": 4,
                        "retention": 0.75, "charge_efficiency": 0.5, "discharge_efficiency": 0.5},
        }
        self.hour = {
            "electric_load": 2, "heat_load": 4, "price": 25,
            "grid_available": True, "pump_available": False,
            "boiler_available": True, "storage_available": True,
        }
        self.arm = {
            "dispatch": {"charge": 0, "discharge": 1.5, "pump_electricity": 0, "boiler_heat": 2},
            "result": {
                "pump_electricity": 0, "pump_heat": 0, "boiler_heat": 2, "heat_produced": 2,
                "heat_delivered": 3.5, "electricity_purchased": 2, "base_electricity_served": 2,
                "electricity_cost": 50, "boiler_cost": 90, "realized_cost": 140,
                "unmet_electricity": 0, "unmet_heat": 0.5, "heat_balance_residual": 0,
                "electricity_balance_residual": 0,
                "storage": {"opening_soc": 4, "closing_soc": 0, "charge": 0, "discharge": 1.5,
                            "retention_loss": 1, "charge_loss": 0, "discharge_loss": 1.5,
                            "balance_residual": 0},
            },
        }

    def test_independent_hand_worked_loss_and_shortfall(self):
        self.assertEqual(audit_hour(self.config, self.hour, self.arm, 4), 0)

    def test_corrupted_cost_supply_and_terminal_hour_soc_are_detected(self):
        for field, value in (("realized_cost", 139), ("unmet_heat", 0), ("electricity_purchased", 1)):
            with self.subTest(field=field):
                bad = deepcopy(self.arm)
                bad["result"][field] = value
                with self.assertRaisesRegex(ValueError, field):
                    audit_hour(self.config, self.hour, bad, 4)
        bad = deepcopy(self.arm)
        bad["result"]["storage"]["closing_soc"] = 1
        with self.assertRaisesRegex(ValueError, "closing_soc"):
            audit_hour(self.config, self.hour, bad, 4)

    def test_unavailable_pump_is_detected(self):
        self.arm["dispatch"]["pump_electricity"] = 0.1
        with self.assertRaisesRegex(ValueError, "availability"):
            audit_hour(self.config, self.hour, self.arm, 4)

    def test_manifest_bytes_are_pinned(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            manifest = directory / "SHA256SUMS.txt"
            manifest.write_bytes(b"fake manifest\n")
            self.assertEqual(digest(manifest), hashlib.sha256(b"fake manifest\n").hexdigest())
            with self.assertRaisesRegex(ValueError, "recorded digest"):
                verify_manifest(directory)


if __name__ == "__main__":
    unittest.main()
