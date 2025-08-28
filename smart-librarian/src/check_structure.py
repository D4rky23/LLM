"""Import-check script for the project packages."""

import importlib
import sys

MODULES_TO_CHECK = [
    "core.config",
    "core.schema",
    "core.data_loader",
    "core.retriever",
    "vector.embeddings",
    "vector.vector_store",
    "ai.tools",
    "ai.llm",
    "interfaces.chatbot_cli",
]

failures = []

for mod in MODULES_TO_CHECK:
    try:
        importlib.import_module(mod)
        print(f"OK: {mod}")
    except Exception as e:
        print(f"FAIL: {mod} -> {e}")
        failures.append((mod, str(e)))

if failures:
    print(f"\n{len(failures)} modules failed to import")
    sys.exit(1)

print("All modules import OK")
