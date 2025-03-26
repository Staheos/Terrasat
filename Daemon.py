import os
import psutil
import datetime
import subprocess
import time

def log(message: any):
    try:
        with open('/home/daemon.log', 'a') as f:
            message = "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "]  " + str(message)
            print(message)
            f.write(message + '\n')
    except Exception as e:
        print(f"log() error: {e}")

while True:
    # List all process IDs
    pids = psutil.pids()
    log(pids)

    gps_running = False
    bmp_running = False

    for pid in pids:
        p = psutil.Process(pid)
        log(p.name())
        if (p.name() != "python3"):
            continue
        log(p.cmdline())

        if "/home/dietpi/gps.py" in p.cmdline():
            log("GPS process found")
            gps_running = True

        if "/home/dietpi/sens/bmp.py" in p.cmdline():
            log("BMP process found")
            bmp_running = True

    if gps_running:
        log("GPS already running")
    else:
        log("GPS process not found, starting it")
        os.popen("sudo python3 /home/dietpi/gps.py")

    if bmp_running:
        log("BMP already running")
    else:
        log("BMP process not found, starting it")
        # os.popen("sudo /home/dietpi/sens/env/bin/python3 /home/dietpi/sens/bmp.py")

    time.sleep(5)


        # subprocess.Popen("python3 /home/dietpi/gps.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    # Check if a specific PID exists
    # pid = 22280
    # if psutil.pid_exists(pid):
    #     p = psutil.Process(pid)
    #     print(p.name())
    #     print(p.cmdline())
    #     p.terminate()
    #     p.wait()

    # Search and kill processes with 'nginx' in their name or command line
    # for p in psutil.process_iter():
    #     try:
    #         if 'nginx' in p.name() or 'nginx' in ' '.join(p.cmdline()):
    #             p.terminate()
    #             p.wait()
    #     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
    #         pass