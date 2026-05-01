import os
import sys
import traceback

# Check env vars
required = ["GOOGLE_API_KEY", "MONGO_URI", "JWT_SECRET"]
missing = [k for k in required if not os.getenv(k)]
if missing:
    print(f"❌ Missing env vars: {missing}", flush=True)
    sys.exit(1)

print(f"✅ PORT = {os.getenv('PORT', 'NOT SET')}", flush=True)
print(f"✅ PYTHON = {sys.version}", flush=True)

# Test importing main and all dependencies
print("🔍 Testing imports...", flush=True)
try:
    import main
    print("✅ main.py imported OK", flush=True)
except Exception as e:
    print(f"❌ Import failed: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

# Test MongoDB connection directly
print("🔍 Testing MongoDB...", flush=True)
try:
    import asyncio
    from database import init_db
    asyncio.run(init_db())
    print("✅ MongoDB connected OK", flush=True)
except Exception as e:
    print(f"❌ MongoDB failed: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

print("✅ All checks passed - starting uvicorn", flush=True)
