import os


def main():
    print(f"PID: {os.getpid()}")
    print(f"Parent PID: {os.getppid()}")

    print("\nEnvironment variables:")
    for key, value in os.environ.items():
        print(f"{key}={value}")

    print("\nOpen file descriptors:")
    try:
        descriptors = os.listdir("/proc/self/fd")
        for descriptor in descriptors:
            print(f"File descriptor: {descriptor}")
    except OSError as error:
        print(f"Could not list file descriptors: {error}")


if __name__ == "__main__":
    main()
