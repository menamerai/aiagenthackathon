#!/usr/bin/env python3
"""
Simple setup verification for Global News Room workflow.
This script checks that all required dependencies and environment variables are available.
"""

import os
import sys

def check_environment_variables():
    """Check if required environment variables are set."""
    print("🔑 Checking environment variables...")
    
    required_vars = {
        'NVIDIA_API_KEY': 'NVIDIA NIM API key for LLM models',
        'TAVILY_API_KEY': 'Tavily API key for web search'
    }
    
    missing = []
    for var, description in required_vars.items():
        if os.getenv(var):
            print(f"  ✅ {var}: Set")
        else:
            print(f"  ❌ {var}: Missing ({description})")
            missing.append(var)
    
    return len(missing) == 0

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    required = (3, 11)
    
    if version >= required:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}: Compatible")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro}: Requires Python {required[0]}.{required[1]}+")
        return False

def check_imports():
    """Check if required packages are installed."""
    print("📦 Checking package imports...")
    
    required_packages = [
        ('pydantic', 'Core dependency'),
        ('asyncio', 'Async support'),
        ('logging', 'Logging support'),
    ]
    
    missing = []
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: Available")
        except ImportError:
            print(f"  ❌ {package}: Missing ({description})")
            missing.append(package)
    
    return len(missing) == 0

def main():
    """Main verification function."""
    print("🌍 Global News Room Setup Verification")
    print("=" * 60)
    
    all_checks = [
        check_python_version(),
        check_environment_variables(),
        check_imports(),
    ]
    
    print("\n📋 Summary:")
    if all(all_checks):
        print("✅ All checks passed! Your setup looks good.")
        print("\n🚀 Next steps:")
        print("1. Install the global news room workflow:")
        print("   cd global_news_room && uv pip install -e .")
        print("\n2. Install AIQ toolkit with LangChain support:")
        print("   cd .. && uv pip install -e '.[langchain]'")
        print("\n3. Run the workflow:")
        print("   aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input 'Your news topic'")
        return 0
    else:
        print("❌ Some checks failed. Please address the issues above.")
        print("\n🔧 Quick fixes:")
        print("• Set environment variables: export NVIDIA_API_KEY='your_key' TAVILY_API_KEY='your_key'")
        print("• Get NVIDIA API key: https://build.nvidia.com")
        print("• Get Tavily API key: https://tavily.com")
        return 1

if __name__ == "__main__":
    exit(main()) 