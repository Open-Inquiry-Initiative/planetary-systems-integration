"""V3-A10 deterministic wire accounting and separately measured local execution.

This harness does not assert equal-information acquisition costs or network latency.
It counts serialized payload bytes for a defined two-message bilateral protocol and
one coordinator request/response protocol. Timing is local process execution only.
"""
import json
from time import perf_counter_ns
from v3a_fixture import Fixture, central_dispatch
from v3a_bounded_protocol import bilateral_one_round

def wire_bytes(message):
    return len(json.dumps(message, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))

def bilateral_wire(price, fixture=Fixture()):
    result = bilateral_one_round(price, fixture)
    messages = [
        {"from": "A", "to": "B", "kind": "offer", "price": price},
        {"from": "B", "to": "A", "kind": "response",
         "accepted": result["messages"][1].kind == "accept"},
    ]
    return {"result": result["dispatch"], "messages": messages,
            "message_count": len(messages),
            "payload_bytes": sum(map(wire_bytes, messages))}

def coordinator_wire(fixture=Fixture()):
    # Both policies are stipulated to know fixture inputs before decisions.
    # This request/response is a dispatch interface, not equivalent information transfer.
    messages = [
        {"from": "A", "to": "C", "kind": "dispatch_request"},
        {"from": "C", "to": "A", "kind": "dispatch_result",
         "flow": central_dispatch(fixture)["flow"]},
    ]
    return {"result": central_dispatch(fixture), "messages": messages,
            "message_count": len(messages),
            "payload_bytes": sum(map(wire_bytes, messages))}

def timed_sample(fn, iterations=1000):
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("iterations must be positive")
    start = perf_counter_ns()
    for _ in range(iterations):
        fn()
    elapsed = perf_counter_ns() - start
    return {"iterations": iterations, "total_ns": elapsed,
            "average_ns": elapsed / iterations}

def comparison(price=40, fixture=Fixture()):
    b = bilateral_wire(price, fixture)
    c = coordinator_wire(fixture)
    return {"bilateral": b, "coordinator": c,
            "payload_byte_delta_bilateral_minus_coordinator": b["payload_bytes"] - c["payload_bytes"],
            "gross_operating_gap": b["result"]["cost"] - c["result"]["cost"],
            "caveat": "Payload bytes are protocol-specific; local timing excludes transport and queueing. Not an equal-resource causal comparison."}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--iterations", type=int, default=1000)
    args = p.parse_args()
    print(json.dumps({"comparison": comparison(),
        "timing": {"bilateral": timed_sample(lambda: bilateral_wire(40), args.iterations),
                   "coordinator": timed_sample(coordinator_wire, args.iterations)}},
        sort_keys=True, indent=2))
