# utils/compat.py
"""
Compatibility shim to restore a few removed symbols for older code:
 - langgraph.checkpoint.base.CheckpointAt
 - langchain.agents.initialize_agent / AgentType (wrap to available constructors)
 - langchain_text_splitters module alias
 - Provide a Tool fallback compatible with langchain_core / langgraph tool conversion
Place this file early in your app startup to avoid changing the rest of your code.
Remove after you pin dependencies / migrate.
"""
import importlib
from dataclasses import dataclass
import sys
from typing import Any, Callable, Optional

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
agents_mod = None
try:
    agents_mod = importlib.import_module("langchain.agents")
except Exception:
    agents_mod = None

if agents_mod is not None and not hasattr(agents_mod, "initialize_agent"):
    # prefer create_react_agent or create_agent if available
    if hasattr(agents_mod, "create_react_agent"):
        def initialize_agent(tools, llm, **kwargs):
            try:
                return agents_mod.create_react_agent(llm=llm, tools=tools, **kwargs)
            except TypeError:
                return agents_mod.create_react_agent(llm, tools, **kwargs)
        setattr(agents_mod, "initialize_agent", initialize_agent)
    elif hasattr(agents_mod, "create_agent"):
        def initialize_agent(tools, llm, **kwargs):
            # create_agent signatures vary. Try common forms progressively.
            try:
                return agents_mod.create_agent(model=llm, tools=tools, **kwargs)
            except TypeError:
                try:
                    return agents_mod.create_agent(llm, tools, **kwargs)
                except TypeError:
                    # last-resort: call with only (tools, llm) positional if supported
                    return agents_mod.create_agent(tools, llm)
        setattr(agents_mod, "initialize_agent", initialize_agent)

    # ensure AgentType namespace exists with ZERO_SHOT_REACT_DESCRIPTION fallback
    if not hasattr(agents_mod, "AgentType"):
        class _AgentType:
            ZERO_SHOT_REACT_DESCRIPTION = "ZERO_SHOT_REACT_DESCRIPTION"
        setattr(agents_mod, "AgentType", _AgentType)

# ---- 3) Provide langchain_text_splitters module alias if layout differs ----
if "langchain_text_splitters" not in sys.modules:
    try:
        import langchain_text_splitters as _mod  # preferred
        sys.modules["langchain_text_splitters"] = _mod
    except Exception:
        try:
            import langchain.text_splitters as _mod2
            sys.modules["langchain_text_splitters"] = _mod2
        except Exception:
            pass

# ---- 4) Provide a Tool-compatible fallback that subclasses BaseTool if available ----
def _install_compat_tool():
    """
    Ensure langchain.tools.Tool and langchain.agents.Tool exist and are compatible.
    If the real BaseTool is available, define CompatTool subclassing it so create_tool
    and create_agent won't try to convert or reject our tool instances.
    """
    FoundBaseTool = None
    # Try common locations for BaseTool
    for loc in ("langchain.tools", "langchain_core.tools.base", "langchain_core.tools"):
        try:
            mod = importlib.import_module(loc)
            if hasattr(mod, "BaseTool"):
                FoundBaseTool = getattr(mod, "BaseTool")
                break
        except Exception:
            continue

    # If we found BaseTool, create a subclass wrapper
    if FoundBaseTool is not None:
        BaseTool = FoundBaseTool
        class CompatTool(BaseTool):
            def __init__(self, name: str, func: Callable[..., Any], description: Optional[str] = None):
                # Some BaseTool implementations take different init signatures.
                # We preserve attributes and implement _run/_arun if required.
                try:
                    super().__init__(name=name, description=description)  # try common signature
                except Exception:
                    # fallback: call without args if BaseTool requires none
                    try:
                        super().__init__()
                    except Exception:
                        pass
                self.name = name
                self.description = description
                self._func = func

            def _run(self, *args, **kwargs):
                return self._func(*args, **kwargs)

            async def _arun(self, *args, **kwargs):
                # if async behavior is needed, run sync function in sync manner
                return self._func(*args, **kwargs)

        # expose CompatTool as Tool in langchain.tools and langchain.agents
        try:
            import langchain.tools as _lt
            if not hasattr(_lt, "Tool"):
                setattr(_lt, "Tool", CompatTool)
        except Exception:
            pass
        try:
            import langchain.agents as _la
            if not hasattr(_la, "Tool"):
                setattr(_la, "Tool", CompatTool)
        except Exception:
            pass
        return

    # If BaseTool not found, fall back to a minimal runtime wrapper that is a simple object
    # but with a callable interface. This is less ideal but prevents immediate crashes.
    @dataclass
    class SimpleTool:
        name: str
        func: Callable[..., Any]
        description: Optional[str] = None

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

    try:
        import langchain.tools as _lt2
        if not hasattr(_lt2, "Tool"):
            setattr(_lt2, "Tool", SimpleTool)
    except Exception:
        pass
    try:
        import langchain.agents as _la2
        if not hasattr(_la2, "Tool"):
            setattr(_la2, "Tool", SimpleTool)
    except Exception:
        pass

# Run the Tool compatibility installer
_install_compat_tool()

# End of compat.py