from .tracer import global_tracer

def pytest_configure(config):
    global_tracer.start()

def pytest_unconfigure(config):
    global_tracer.stop()
