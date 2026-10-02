import os
import shlex
import signal


jobs = {}
next_job_id = 1


def reap_jobs():
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            break

        if pid == 0:
            break

        for job_id, job in list(jobs.items()):
            if job["pid"] == pid:
                if os.WIFSIGNALED(status):
                    del jobs[job_id]
                else:
                    job["status"] = "Done"
                break


def main():
    global next_job_id

    while True:
        reap_jobs()

        try:
            line = input("myshell> ")
        except EOFError:
            break

        reap_jobs()

        try:
            args = shlex.split(line)
        except ValueError:
            print("myshell: invalid quotes")
            continue

        if not args:
            continue

        background = args[-1] == "&"
        if background:
            args.pop()
        if not args:
            continue

        command = args[0]

        if command == "exit":
            break

        elif command == "cd":
            try:
                directory = args[1] if len(args) > 1 else os.environ["HOME"]
                os.chdir(directory)
            except OSError as error:
                print(f"myshell: {error}")

        elif command == "jobs":
            for job_id, job in list(jobs.items()):
                print(f'[{job_id}]  {job["status"]:<10} {job["command"]}')
                if job["status"] == "Done":
                    del jobs[job_id]

        elif command == "fg" or command == "kill":
            try:
                job_id = int(args[1])
                job = jobs[job_id]
                if job["status"] == "Done":
                    print("myshell: job already fiinished")
                    continue

                if command == "fg":
                    print(job["command"], flush=True)
                    os.waitpid(job["pid"], 0)
                else:
                    os.kill(job["pid"], signal.SIGTERM)
                    os.waitpid(job["pid"], 0)
                    print(f'[{job_id}]  Terminated  {job["command"]}')

                del jobs[job_id]
            except (IndexError, ValueError, KeyError):
                print("myshell: enter a valid job number")
            except (ProcessLookupError, ChildProcessError):
                jobs.pop(job_id, None)
                print("myshell: job already finish")

        else:
            try:
                pid = os.fork()
            except OSError as error:
                print(f"myshell: {error}")
                continue

            if pid == 0:
                try:
                    os.execvp(command, args)
                except FileNotFoundError:
                    print(f"myshell: {command}: comand not found", flush=True)
                except OSError as error:
                    print(f"myshell: {error}", flush=True)
                os._exit(1)

            elif background:
                text = " ".join(args)
                jobs[next_job_id] = {
                    "pid": pid,
                    "command": text,
                    "status": "Running"
                }
                print(f"[{next_job_id}] {pid} {text}")
                next_job_id += 1

            else:
                os.waitpid(pid, 0)


if __name__ == "__main__":
    main()

