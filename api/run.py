import os
import argparse
import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Whisky Bottle Recognition API")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Server port")
    parser.add_argument("--reload", "-r", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.path.abspath('.')
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    ) 