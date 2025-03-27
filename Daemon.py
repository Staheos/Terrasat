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

def kill_process(pid: int = -1, name: str = "this should never be in any of the process names"):
    try:
        for p in psutil.process_iter():

            if p.pid == pid or name in p.name() or name in ' '.join(p.cmdline()):
                p.terminate()
                p.wait(1)
    except Exception as e:
        log(f"kill_process() error: {e}")

while True:
    # time.sleep(5)

    communication_running = False
    bmp_running = False
    laser_running = False
    bno_running = False
    gps_running = False

    try:
        # List all process IDs
        pids = psutil.pids()
        log(pids)

        for pid in pids:
            p = psutil.Process(pid)
            if (p.name() != "python3"):
                continue
            log(p.name())
            log(p.cmdline())

            for arg in p.cmdline():
                if "server.py" in arg:
                    log("Communication process found")
                    communication_running = True

                if "bmp.py" in arg:
                    log("BMP process found")
                    bmp_running = True

                if "LASER.py" in arg:
                    log("Laser process found")
                    laser_running = True

                if "bno.py" in arg:
                    log("BNO process found")
                    bno_running = True

                if "gps.py" in arg:
                    log("GPS process found")
                    gps_running = True
    except Exception as e:
        log(f"Error checking processes: {e}")
        continue

    if communication_running:
        log("Communication already running")
    else:
        log("Starting communication process")
        os.popen("cd /home/dietpi/Communication && sudo python3 server.py &")
        # subprocess.Popen()
        time.sleep(5)

    if bmp_running:
        log("BMP already running")
    else:
        log("Starting BMP process")
        os.popen("cd /home/dietpi/bmp && sudo python3 bmp.py &")
        time.sleep(5)

    if laser_running:
        log("Laser already running")
    else:
        log("Starting Laser process")
        # os.popen("cd /home/dietpi/laser && sudo python3 LASER.py &")
        # time.sleep(5)

    if bno_running:
        log("BNO already running")
    else:
        log("Starting BNO process")
        # os.popen("cd /home/dietpi/bno && sudo python3 bno.py &")
        # time.sleep(5)

    if gps_running:
        log("GPS already running")
    else:
        log("Starting GPS process")
        os.popen("cd /home/dietpi/gps && sudo python3 gps.py &")
        time.sleep(5)

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