"""GDPR policy routing only; applications execute returned action plans."""

import json
import math
import os
from typing import Any
from urllib.request import Request, urlopen


USER_POLICIES = {
    "consent": "consent.may_process_or_store",
    "lawful": "lawful.lawful_processing",
    "information": "information.information",
    "access": "access.access_response",
    "rectification": "rectification.rectification_response",
}
REQUEST_POLICIES = {
    "erasure": "erasure", "restriction": "restriction", "portability": "portability",
    "objection": "objection", "breach": "breach", "complaint": "complaint",
}


class GdprRouter:
    def __init__(self, url: str | None = None, timeout_ms: float = 10000):
        if (isinstance(timeout_ms, bool) or not isinstance(timeout_ms, (int, float))
                or not math.isfinite(timeout_ms) or timeout_ms <= 0):
            raise ValueError("Invalid timeout")
        self.url = url if url is not None else os.environ.get("OPA_QUERY_URL", "http://localhost:8181/v1/query")
        self.timeout_ms = timeout_ms

    def query(self, expression: str, input_data: dict) -> Any:
        payload = json.dumps({"query": "x := " + expression, "input": input_data}).encode("utf-8")
        request = Request(self.url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout_ms / 1000) as response:
            body = json.load(response)
        if not isinstance(body, dict) or ("result" in body and not isinstance(body["result"], list)):
            raise ValueError("Invalid OPA response")
        rows = body.get("result", [])
        if not rows:
            return None
        if not isinstance(rows[0], dict):
            raise ValueError("Invalid OPA response")
        return rows[0].get("x")

    def route(self, policy: str, input_data: dict, user_id: str | None = None) -> Any:
        if not isinstance(input_data, dict):
            raise TypeError("input must be a JSON object")
        if not isinstance(policy, str):
            raise TypeError("policy must be a string")
        if policy in USER_POLICIES:
            if not isinstance(user_id, str) or not user_id:
                raise TypeError("user_id must be a nonempty string")
            # Encode IDs as Rego string literals, never interpolate raw input.
            value = self.query(f"data.{USER_POLICIES[policy]}({json.dumps(user_id)})", input_data)
            return value if value is not None else (False if policy in ("consent", "lawful") else {})
        if policy not in REQUEST_POLICIES:
            raise ValueError(f"Unknown policy: {policy}")
        prefix = "data." + REQUEST_POLICIES[policy]
        decision = self.query(prefix + ".decision", input_data)
        justification = self.query(prefix + ".justification", input_data)
        actions = self.query(prefix + ".actions", input_data)
        return {
            "decision": decision if decision is not None else ("no_notify" if policy == "breach" else "reject"),
            "justification": justification if justification is not None else [],
            "actions": actions if actions is not None else {},
        }
