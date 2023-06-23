import os
import socket
import shutil
import subprocess
import time

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

route = os.getenv('ROUTE')
if route is None:
    route = '/'
listen_host = os.getenv('LISTEN_IP')
if listen_host is None:
    listen_host = 'localhost'
listen_port = os.getenv('LISTEN_PORT')
if listen_port is None:
    listen_port = 9002
else:
    listen_port = int(listen_port)

if os.getenv('DEBUG') == 'False':
    debug_mode = False
elif os.getenv('DEBUG') == 'True':
    debug_mode = True
else:
    debug_mode = False

display_host = listen_host
if display_host == '0.0.0.0' or display_host == 'localhost':
    display_host = socket.gethostbyname(socket.gethostname())

watchdog_file = os.getenv('WATCHDOG_TIMEFILE')
if watchdog_file is None:
    watchdog_file = '.pywatchdog'
logs_folder = os.getenv('LOGS_FOLDER')
if logs_folder is None:
    logs_folder = 'logs'

while True:
    print(
        f'\nStarting GPT4All API listener for single request on {display_host}:{listen_port}{route}\n')
    p = subprocess.Popen(["python", "server.py"], shell=False)

    file_not_found_counter = 0

    while True:
        if not os.path.exists(watchdog_file):
            file_not_found_counter += 1
            time.sleep(1)  # increment counter and wait for 1 second
        else:
            file_not_found_counter = 0  # reset counter if file found

        if file_not_found_counter > 5:  # if file not found for more than 5 seconds
            break

    while not os.path.exists(watchdog_file):

        print("[SUCCESS]  Server completed request!  Restarting server in 5 seconds...")
        time.sleep(5)
        skip_log_file = False

        if os.path.exists(watchdog_file):
            print(
                "[SUCCESS]  Server completed request!  Restarting server in 5 seconds...")
            os.remove(watchdog_file)
            time.sleep(5)
        else:
            skip_log_file = False
            error_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            if not os.path.exists(logs_folder):
                try:
                    os.makedirs(logs_folder)
                except Exception as e:
                    print(
                        f'[ERROR] [{error_time}] Could not create logs folder: {e}]')
                    skip_log_file = True
            print(
                '[ERROR] Something went wrong with watchdog... Restarting server in 5 seconds...')
            if skip_log_file is False:
                if os.path.exists(watchdog_file):
                    create_time = os.path.getctime(watchdog_file)
                    create_time_str = datetime.fromtimestamp(
                        create_time).strftime('%Y%m%d_%H%M%S')
                    error_file = f'{create_time_str}_watchdog_error.log'
                    error_file_path = f'{logs_folder}/{error_file}'
                    shutil.copy(watchdog_file, error_file_path)
                    time.sleep(2)
                    os.remove(watchdog_file)
                    time.sleep(3)
            else:
                time.sleep(5)
            break
