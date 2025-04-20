#!/usr/bin/env python3
"""
Setup script for Whisky Bottle Recognition API.
Creates necessary directories and verifies dependencies.
"""

import os
import sys
import shutil
import subprocess
import pkg_resources

# Directories to create
DIRS = [
    "data",
    "data/embeddings",
    "static",
    "static/images",
    "logs"
]

def check_python_version():
    """Check if Python version is 3.9 or higher."""
    required_version = (3, 9)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}.{current_version[2]}")
        return False
    
    print(f"Python version {current_version[0]}.{current_version[1]}.{current_version[2]} ✅")
    return True

def create_directories():
    """Create necessary directories."""
    for directory in DIRS:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory} ✅")

def check_dependencies():
    """Check if all dependencies are installed."""
    with open("requirements.txt", "r") as f:
        requirements = [line.strip() for line in f if line.strip()]
    
    missing = []
    for requirement in requirements:
        try:
            req = pkg_resources.Requirement.parse(requirement)
            pkg_resources.get_distribution(req)
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            missing.append(requirement)
    
    if missing:
        print("Missing dependencies:")
        for package in missing:
            print(f"  - {package}")
        print("\nInstall them with:")
        print("  pip install -r requirements.txt")
        return False
    
    print("All dependencies are installed ✅")
    return True

def test_imports():
    """Test importing critical packages."""
    try:
        import torch
        import faiss
        import transformers
        import fastapi
        print("Critical imports successful ✅")
        return True
    except ImportError as e:
        print(f"Error importing packages: {e}")
        return False

def main():
    """Run setup checks and initialization."""
    print("=" * 50)
    print("Whisky Bottle Recognition API - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        print("\nWarning: Some dependencies are missing. Install them before running the API.")
    
    # Test imports
    if not test_imports():
        print("\nError: Critical imports failed. Check your installation.")
        sys.exit(1)
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Process your bottle dataset:")
    print("   python process_dataset.py --input /path/to/images --output data/embeddings --metadata data/metadata.json --copy-images")
    print("2. Start the API:")
    print("   python run.py")
    print("\nOr use Docker:")
    print("   docker-compose up -d")
    
if __name__ == "__main__":
    main() 