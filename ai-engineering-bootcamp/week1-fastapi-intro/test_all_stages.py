import json
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"


def request_json(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request) as response:
        return json.loads(response.read())


def main() -> None:
    assert request_json("/")["status"] == "ok"
    result = request_json(
        "/ask",
        method="POST",
        body={"question": "Reply with a short greeting."},
    )
    required = {"answer", "tokens_used", "cost_usd"}
    assert required.issubset(result), f"Missing fields: {required - result.keys()}"
    print("PASS: health check")
    print("PASS: /ask response contains answer, tokens_used, and cost_usd")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()