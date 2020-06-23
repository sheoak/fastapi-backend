from app.core import config


def tweak_config(key, value):
    """Change the configuration and set it back after"""
    before = getattr(config, key)
    setattr(config, key, value)
    yield config
    setattr(config, key, before)
