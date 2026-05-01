import os
import sys
import traceback

required = ["GOOGLE_API_KEY", "MONGO_URI", "JWT_SECRET"]
missing = [k for k in required if not os.getenv(k)]
if missing:
    print(f"❌ Missing env vars: {missing}", flush=True)
    sys.exit(1)

print(f"✅ PORT = {os.getenv('PORT', 'NOT SET')}", flush=True)
print(f"✅ PYTHON = {sys.version}", flush=True)

# Test each import individually
print("🔍 Testing imports one by one...", flush=True)

modules = [
    "fastapi", "motor", "pydantic", "jose",
    "passlib", "dotenv", "langchain_google_genai",
    "pdfplumber", "aiofiles", "redis"
]
for mod in modules:
    try:
        __import__(mod)
        print(f"  ✅ {mod}", flush=True)
    except Exception as e:
        print(f"  ❌ {mod}: {e}", flush=True)

# Now try main.py
print("🔍 Importing main.py...", flush=True)
try:
    import main
    print("✅ main.py OK", flush=True)
except Exception as e:
    print(f"❌ main.py FAILED: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

print("✅ All checks passed!", flush=True)
