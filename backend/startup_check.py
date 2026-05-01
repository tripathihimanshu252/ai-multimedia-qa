import os
import sys

required = ["GOOGLE_API_KEY", "MONGO_URI", "JWT_SECRET"]
missing = [k for k in required if not os.getenv(k)]

if missing:
    print(f"❌ FATAL: Missing environment variables: {missing}", flush=True)
    sys.exit(1)

print(f"✅ All env vars present", flush=True)
print(f"✅ GOOGLE_API_KEY starts with: {os.getenv('GOOGLE_API_KEY', '')[:10]}...", flush=True)
print(f"✅ MONGO_URI starts with: {os.getenv('MONGO_URI', '')[:30]}...", flush=True)
