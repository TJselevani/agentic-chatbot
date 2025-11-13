AGENT_REGISTRY = {}


def register_agent(name):
    def decorator(cls_or_func):
        AGENT_REGISTRY[name] = cls_or_func
        return cls_or_func

    return decorator
