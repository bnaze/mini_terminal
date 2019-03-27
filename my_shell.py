#! /usr/bin/env python
import subprocess
import os, sys
import signal
import shutil
import pwd
from datetime import datetime
# The purpose of this script is to give you simple functions for locating an executable program in common locations in the Linux path

# Simple shell
# COMMANDS          ERRORS CHECKED
# 1. info XX         - check file/dir exists
# 2. files
# ... omitted for simplicity
# 8. Default is to run the program


# Here the path is hardcoded, but you can easily optionally get your PATH environ variable
# by using: path = os.environ['PATH'] and then splitting based on ':' such as the_path = path.split(':')
THE_PATH = ["/bin/", "/usr/bin/", "/usr/local/bin/", "./"]

# ========================
#    Run command
#    Run an executable somewhere on the path
#    Any number of arguments
# ========================
def runCmd(fields):
  global PID, THE_PATH

  cmd = fields[0]
  cnt = 0
  args = []
  while cnt < len(fields):
      args.append(fields[cnt])
      cnt += 1

  execname = add_path(cmd, THE_PATH)
  print(execname)

  # run the executable
  if not execname:
      print('Executable file ' + str(cmd) +' not found')
      return

  # execv executes a new program, replacing the current process; on success, it does not return.
  # On Unix, the new executable is loaded into  the current process, and will have the same process id as the caller.
  PID = os.fork() #current process pid
  if PID == 0:
      try:
          #print(PID, "I am in the child")
          os.execv(execname, args)
          os._exit(0)
      except:
          print('Something went wrong there')
          return
  else:
      #print(PID, "I am in the parent")
      _, status = os.waitpid(0, 0)
      exitCode = os.WEXITSTATUS(status)
      print("Child exit code is: %d" % (exitCode))

# ========================
#    Constructs the full path used to run the external command
#    Checks to see if the file is executable
# ========================
def add_path(cmd, path):
    if cmd[0] not in ['/', '.']:
        for d in path:
            execname = d + cmd
            if os.path.isfile(execname) and os.access(execname, os.X_OK):
                return execname
        return False
    else:
        return cmd

# ========================
#    files command
#    List file and directory names
#    No arguments
# ========================
def filesCmd(fields):
    path = fields[0]

    for filename in os.listdir('.'):
        if(os.path.isfile(filename) == False):
            print(filename,"(D)")
        else:
            print(filename)


# ========================
#  info command
#     List file information
#     1 argument: file name
# ========================
def infoCmd(fields):
    #checking if file exists
    fileExists = os.path.exists(fields)

    if(fileExists == False):
        print("File does not exist")
        return

    isFile = os.path.isfile(fields)
    st = os.stat(fields)
    size = None

    #If file exists, find if it is a file/dir
    if(isFile==True):
        print("File: Regular File")
        size = "Size: " + str(st.st_size) + " bytes"
    else:
        print("File: Directory")

    #display information here
    ownerID = st.st_uid
    print("Owner ID:", ownerID)
    print("Owner:", pwd.getpwuid(ownerID).pw_name)
    print("Last Changed:", datetime.fromtimestamp(st.st_mtime))

    #prints only if field is a file
    if(size != None):
        print(size)
        print("Is Exec:", os.access(fields, os.X_OK))

def delete_file(fields):
    #check args here
    if(checkArgs(fields,1) == False):
        return

    filename = fields[1]

    if(os.path.exists(filename) == False):
        print("File does not exist")
        return
    else:
        os.remove(filename)

def copy_file(fields):
    if(fields[1] == None or fields[2] == None):
        print("Missing args")
        return

    for filename in os.listdir('.'):
        if filename == fields[2]:
            print("File already exists")
            return
    shutil.copyfile(fields[1],fields[2])

def where():
    dir = os.getcwd()
    print(dir)
    return dir

def up(fields):
    try:
        currentDir = os.getcwd()
        splitCurrentDir = currentDir.split("/")
        upDir = ""

        for i in range(1,len(splitCurrentDir)-1):
            upDir = upDir + "/" + splitCurrentDir[i]

        os.chdir(upDir)
    except:
        print("Can't go further up")
        return

    #Testing purposes here
    #print(os.getcwd())

def down(fields):
    if(checkArgs(fields,1) == False):
        return

    dirName = fields[1]

    if(os.path.isdir(dirName) == False):
        print("Not a dir")
    else:
        changeTo = os.getcwd()
        changeTo = changeTo + "/" + dirName
        os.chdir(changeTo)

        #Testing done here
        #print(os.getcwd())
# ----------------------
# Other functions
# ----------------------
def checkArgs(fields, num):
    numArgs = len(fields) - 1
    if numArgs == num:
        return True
    if numArgs > num:
        print("  Unexpected argument " + fields[num+1] + "for command " + fields[0])
    else:
        print( "  Missing argument for command " + fields[0])

    return False

# define the singal handler to modify standard behaviour when the process catches the SIGINT signal (CTRL-C)
def sigint_handler(signum, frame):
    global PID, hasChild

    if hasChild == True:
        print("Loading the gun and killing this fucking child")
        os.kill(PID,signal.SIGKILL)
    print("No child")

#Install the signal handler
signal.signal(signal.SIGINT, sigint_handler)

# ----------------------------------------------------------------------------------------------------------------------
while True:
        global hasChild
        hasChild=False

        line = input("PShell>")  # NOTE! This is only for python 2. Should be 'input' for python 3
        fields = line.split()

        if fields[0] == "files":
            filesCmd(fields)
        elif fields[0] == "info":
            if(checkArgs(fields,1) == False):
                continue
            infoCmd(fields[1])
        elif fields[0] == "delete":
            delete_file(fields)
        elif fields[0] == "copy":
            if(len(fields) >=4):
                print("Too many args")
            copy_file(fields)
        elif fields[0] == "where":
            where()
        elif fields[0] == "down":
            down(fields)
        elif fields[0] == "up":
            #checkArgs(fields[1])
            up(fields)
        elif fields[0] == "finish":
            os._exit(0)
        else:
            hasChild = True
            runCmd(fields)
