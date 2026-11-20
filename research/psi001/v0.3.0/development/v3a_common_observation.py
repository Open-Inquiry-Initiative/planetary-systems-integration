"""V3-A13 common observation and symmetric accounting experiment.

Each policy receives the identical snapshot payload from a neutral observer.
Dispatch exchange messages remain protocol-specific and are separately metered.
This is a deterministic accounting fixture, not a network timing experiment.
"""
import json
from v3a_fixture import Fixture
from v3a_instrumentation import bilateral_wire, coordinator_wire, wire_bytes


def snapshot(f=Fixture()):
    return {"boiler_cost": f.boiler_cost_per_delivered_mwh,
            "demand": f.demand_mwh, "efficiency": f.delivery_efficiency,
            "link_capacity": f.link_capacity_mwh,
            "pumping_cost": f.pumping_cost_per_input_mwh,
            "surplus": f.surplus_mwh}


def observe(policy, f=Fixture()):
    if policy not in ("bilateral", "coordinator"):
        raise ValueError("unknown policy")
    message = {"from": "observer", "to": policy, "kind": "snapshot", "data": snapshot(f)}
    return {"message": message, "bytes": wire_bytes(message)}


def compare(price=40, f=Fixture()):
    b, c = bilateral_wire(price, f), coordinator_wire(f)
    bo, co = observe("bilateral", f), observe("coordinator", f)
    # Sender/recipient identifiers differ in length. Canonicalize the common
    # payload separately rather than falsely claiming equal envelope bytes.
    canonical_snapshot_bytes = len(json.dumps(snapshot(f), sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8"))
    return {
        "common_snapshot_payload_bytes_each": canonical_snapshot_bytes,
        "bilateral": {"observation_envelope_bytes": bo["bytes"],
                      "decision_payload_bytes": b["payload_bytes"],
                      "total_messages": b["message_count"] + 1,
                      "operating_cost": b["result"]["cost"]},
        "coordinator": {"observation_envelope_bytes": co["bytes"],
                        "decision_payload_bytes": c["payload_bytes"],
                        "total_messages": c["message_count"] + 1,
                        "operating_cost": c["result"]["cost"]},
        "gross_operating_gap": b["result"]["cost"] - c["result"]["cost"],
        "limits": "Equal snapshot content only. Protocol envelopes, topology, CPU, timing and network cost not equalized."
    }


if __name__ == "__main__":
    print(json.dumps(compare(), indent=2, sort_keys=True))
