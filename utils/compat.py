# utils/compat.py
"""
Compatibility shim to restore a few removed symbols for older code:
 - langgraph.checkpoint.base.CheckpointAt
 - langchain.agents.initialize_agent / AgentType (wrap to available constructors)
 - langchain_text_splitters module alias
Place this file early in your app startup to avoid changing the rest of your code.
Remove after you pin dependencies / migrate.
"""
import importlib
from dataclasses import dataclass
import sys

# ---- 1) Ensure CheckpointAt exists for langgraph imports ----
try:
    base_mod = importlib.import_module("langgraph.checkpoint.base")
except Exception:
    base_mod = None

if base_mod is not None and not hasattr(base_mod, "CheckpointAt"):
    # alias an existing Checkpoint if present
    if hasattr(base_mod, "Checkpoint"):
        setattr(base_mod, "CheckpointAt", getattr(base_mod, "Checkpoint"))
    else:
        @dataclass
        class CheckpointAt:
            """Fallback placeholder for langgraph.checkpoint.base.CheckpointAt"""
            at: int = 0
        setattr(base_mod, "CheckpointAt", CheckpointAt)

# ---- 2) Provide initialize_agent + AgentType if missing from langchain.agents ----
try:
    # try classic import to see if it's already present
    importlib.import_module("langchain.agents")
    agents_mod = importlib.import_module("langchain.agents")
except Exception:
    agents_mod = None

if agents_mod is not None and not hasattr(agents_mod, "initialize_agent"):
    # prefer create_react_agent or create_agent if available
    if hasattr(agents_mod, "create_react_agent"):
        def initialize_agent(tools, llm, **kwargs):
            # adapt common signatures: new constructors often accept llm= or model=
            try:
                return agents_mod.create_react_agent(llm=llm, tools=tools, **kwargs)
            except TypeError:
                return agents_mod.create_react_agent(llm, tools, **kwargs)
        setattr(agents_mod, "initialize_agent", initialize_agent)
    elif hasattr(agents_mod, "create_agent"):
        def initialize_agent(tools, llm, **kwargs):
            try:
                return agents_mod.create_agent(model=llm, tools=tools, **kwargs)
            except TypeError:
                return agents_mod.create_agent(llm, tools, **kwargs)
        setattr(agents_mod, "initialize_agent", initialize_agent)

    # ensure AgentType namespace exists with ZERO_SHOT_REACT_DESCRIPTION fallback
    if not hasattr(agents_mod, "AgentType"):
        class _AgentType:
            ZERO_SHOT_REACT_DESCRIPTION = "ZERO_SHOT_REACT_DESCRIPTION"
        setattr(agents_mod, "AgentType", _AgentType)

# ---- 3) Provide langchain_text_splitters module alias if layout differs ----
# Some installs expose `langchain.text_splitters` or `langchain_text_splitter` (typo). Ensure the plural import works.
if "langchain_text_splitters" not in sys.modules:
    try:
        import langchain_text_splitters as _mod  # preferred
        sys.modules["langchain_text_splitters"] = _mod
    except Exception:
        try:
            import langchain.text_splitters as _mod2
            sys.modules["langchain_text_splitters"] = _mod2
        except Exception:
            # leave absent; missing import will surface later
            pass