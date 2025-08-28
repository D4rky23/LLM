#!/usr/bin/env python3
"""Test script for Smart Librarian CLI"""

import sys
import os

# Add the source directory to Python path
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
)

from src.core.config import config
from src.ai.llm import get_chatbot


def test_cli():
    print("🔧 Testing Smart Librarian CLI components...")

    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    try:
        config.validate()
        print("✅ Configuration is valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

    # Test 2: Chatbot initialization
    print("\n2. Testing Chatbot initialization...")
    try:
        chatbot = get_chatbot()
        print("✅ Chatbot initialized successfully")
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        return False

    # Test 3: Simple chat
    print("\n3. Testing Simple Chat...")
    try:
        response = chatbot.chat(
            "What books do you recommend about friendship?"
        )
        print(f"✅ Chat response received:")
        print(f"📚 {response[:200]}...")
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

    print("\n🎉 All CLI components are working correctly!")
    return True


if __name__ == "__main__":
    test_cli()
