import json
import sys

def main():
    body = json.loads(sys.stdin.read())
    score = body.get("score")
    threshold = body.get("threshold", 70)
    if score is None:
        result = {"passed": False, "reason": "Missing required input: score"}
        print("needs_agent", flush=True)
    elif score >= threshold:
        result = {"passed": True, "reason": f"Score {score} meets or exceeds threshold {threshold}"}
        print(json.dumps(result))
    else:
        result = {"passed": False, "reason": f"Score {score} is below threshold {threshold}"}
        print(json.dumps(result))

if __name__ == "__main__":
    main()
