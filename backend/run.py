#!/usr/bin/env python3
"""
Unified Runner Script

This script provides convenient commands to run the complete RAG system:
1. Ingest content from the textbook website
2. Start the chatbot API server
3. Run both services together

Usage:
    python run.py ingest    # Run content ingestion pipeline
    python run.py api       # Start chatbot API server
    python run.py all       # Run ingestion then start API
    python run.py check     # Check environment configuration
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_ingestion():
    """Run the content ingestion pipeline."""
    print("🚀 Starting content ingestion pipeline...")
    print("This will extract content from the textbook and store it in Qdrant.")
    print()

    try:
        result = subprocess.run([sys.executable, "main.py"], check=True)
        print("✅ Content ingestion completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Content ingestion failed with exit code {e.returncode}")
        return False

def run_api():
    """Start the chatbot API server."""
    print("🤖 Starting chatbot API server...")
    print("API will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print()

    try:
        subprocess.run([sys.executable, "chatbot_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Chatbot API server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ API server failed with exit code {e.returncode}")

def check_environment():
    """Check if environment is properly configured."""
    required_vars = ['COHERE_API_KEY', 'QDRANT_URL', 'QDRANT_API_KEY', 'OPENAI_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please set these in your .env file or environment.")
        print("See README.md for setup instructions.")
        return False

    print("✅ Environment configuration looks good!")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [command]")
        print()
        print("Commands:")
        print("  ingest    Run content ingestion pipeline")
        print("  api       Start chatbot API server")
        print("  all       Run ingestion then start API")
        print("  check     Check environment configuration")
        return

    command = sys.argv[1].lower()

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    if command == "check":
        check_environment()
    elif command == "ingest":
        if not check_environment():
            return
        run_ingestion()
    elif command == "api":
        if not check_environment():
            return
        run_api()
    elif command == "all":
        if not check_environment():
            return

        print("🔄 Running complete RAG system setup...")
        print()

        if run_ingestion():
            print()
            print("⏳ Waiting 3 seconds before starting API...")
            time.sleep(3)
            print()
            run_api()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python run.py' to see available commands")

if __name__ == "__main__":
    main()