from rootcause.tracer import global_tracer


def main():
    global_tracer.start()
    try:
        # Run the command given in arguments, typically like: pytest tests/...
        # But we need to use runpy or something since we're replacing the entrypoint
        # Alternatively, we can inject tracer via a pytest plugin or sitecustomize
        pass
    finally:
        global_tracer.stop()


if __name__ == "__main__":
    main()
