#! /usr/bin/env python3

import os, sys, re

pid = os.getpid()

while 1:
    os.write(1,("$").encode())
    cmd = os.read(0, 50).decode().strip()
    if(cmd == "exit"):
        break

    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                    (os.getpid(), pid)).encode())
        args = ["wc", "p3-exec.py"]

        for i in range(len(args)-1):
            os.close(1)
            fa = str(os.open(args[i+1], os.O_WRONLY | os.O_CREAT))
            os.set_inheritable(1, True)
            n = len(args)
            for j in range(o, n-i):
                args.pop()

        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 

        os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                    (pid, rc)).encode())
        if(not cmd[len(cmd)-1] == "$"):
            childPidCode = os.wait()