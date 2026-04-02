import uvicorn
import os
import subprocess
import sys

def main():
    print("🚀 Starting Personal Finance Tracker (Local Mode)")
    
    # 1. Install missing dependencies if needed
    print("📦 Checking requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"⚠️ Warning: Could not verify requirements: {e}")

    # 2. Set environment variables to trigger SQLite fallback
    # By default, config.py falls back to SQLite if POSTGRES_SERVER is not set
    os.environ["POSTGRES_SERVER"] = "" 
    
    # 3. Start Uvicorn
    print("🌐 Launching API at http://localhost:8000")
    print("📈 Documentation: http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
