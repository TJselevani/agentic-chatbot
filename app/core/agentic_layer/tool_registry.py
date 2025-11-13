# app/core/agentic_layer/tool_registry.py
import pkgutil
import importlib
import inspect
import app.core.agentic_layer.tools as tools_pkg
from app.core.agentic_layer.tools.base_tool import ReusableTool


def get_registered_tools():
    """
    Dynamically discovers and registers all subclasses of ReusableTool
    inside the tools package.
    """
    registered_tools = []

    # Iterate through all modules in the tools package
    for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
        module = importlib.import_module(f"{tools_pkg.__name__}.{module_name}")

        # Inspect classes in each module
        for _, cls in inspect.getmembers(module, inspect.isclass):
            # Ensure it's a subclass of ReusableTool but not the base itself
            if issubclass(cls, ReusableTool) and cls is not ReusableTool:
                try:
                    registered_tools.append(cls())
                except Exception as e:
                    print(f"⚠️ Could not initialize tool {cls.__name__}: {e}")

    return registered_tools
