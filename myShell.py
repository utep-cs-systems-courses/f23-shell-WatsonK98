import os
import sys
import re

pid = os.getpid()

while True:
    os.write(1, ("$").encode())
    input_cmd = os.read(0, 50).decode().strip()
    
    if input_cmd == "exit":
        break

    # Split commands based on pipe symbol '|'
    commands = input_cmd.split('|')

    # Iterate over each command in the pipeline
    prev_read = 0  # File descriptor to read from initially
    for i, cmd in enumerate(commands):
        rc = os.fork()

        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:  # child
            os.write(1, ("Child: My pid==%d. Parent's pid=%d\n" % (os.getpid(), pid)).encode())

            # Redirect input if not the first command
            if i > 0:
                os.dup2(prev_read, 0)
                os.close(prev_read)

            # Redirect output if not the last command
            if i < len(commands) - 1:
                os.dup2(os.pipe()[1], 1)

            # Parse and execute the command
            args = cmd.split()
            for dir in re.split(":", os.environ['PATH']):
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)
                except FileNotFoundError:
                    pass

            os.write(2, ("Child: Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)

        else:  # parent
            os.write(1, ("Parent: My pid=%d. Child's pid=%d\n" % (pid, rc)).encode())
            os.wait()  # Wait for the child process to finish
            prev_read = os.pipe()[0]  # File descriptor to read from next

