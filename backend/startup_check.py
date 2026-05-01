import os
import sys

required = ["GOOGLE_API_KEY", "MONGO_URI", "JWT_SECRET"]
missing = [k for k in required if not os.getenv(k)]

if missing:
    print(f"❌ FATAL: Missing env vars: {missing}", flush=True)
    sys.exit(1)

port = os.getenv("PORT", "NOT SET")
print(f"✅ All env vars present", flush=True)
print(f"✅ PORT = {port}", flush=True)
print(f"✅ PYTHON = {sys.version}", flush=True)

if port == "NOT SET":
    print("❌ PORT not set by Render!", flush=True)
    sys.exit(1)
