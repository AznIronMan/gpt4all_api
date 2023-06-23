import contextlib
import logging
import os
import platform
import shutil
import time

from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from gpt4all import GPT4All

load_dotenv()

instance_date = datetime.now().strftime('%Y%m%d')


def setup_logger():
    log_folder = os.getenv('LOGS_FOLDER')
    if log_folder is None:
        log_folder = 'logs'
    if not os.path.exists(log_folder):
        try:
            os.makedirs(log_folder)
        except Exception as e:
            print(f'[ERROR] Could not create logs folder: {e}]')
            return False
    logging.basicConfig(filename=(f'{log_folder}/gpt4all_api_{instance_date}.log'),
                        level=logging.ERROR, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    return True


logging_mode = setup_logger()

watchdog_file = os.getenv('WATCHDOG_TIMEFILE')
if watchdog_file is None:
    watchdog_file = '.pywatchdog'
logs_folder = os.getenv('LOGS_FOLDER')
if logs_folder is None:
    logs_folder = 'logs'

if os.path.exists(watchdog_file):
    try:
        create_time = os.path.getctime(watchdog_file)
        create_time_str = datetime.fromtimestamp(
            create_time).strftime('%Y%m%d_%H%M%S')
        error_file = f'{create_time_str}_watchdog_error.log'
        error_file_path = f'{logs_folder}/{error_file}'
        shutil.copy(watchdog_file, error_file_path)
        time.sleep(2)
        os.remove(watchdog_file)
        time.sleep(3)
    except Exception as e:
        err_msg = f'[ERROR] Could not rename watchdog file: {e}]'
        if (logging_mode):
            logging.error(err_msg)
        raise SystemExit(err_msg)
    try:
        os.remove(watchdog_file)
    except Exception as e:
        err_msg = f'[ERROR] Could not remove watchdog file: {e}]'
        if (logging_mode):
            logging.error(err_msg)
        raise SystemExit(err_msg)
with open(watchdog_file, 'x') as f:
    f.write(f'Starting: {datetime.now()}\n')

app = Flask(__name__)

model_path = os.getenv('MODEL_PATH')

if model_path is not None and os.path.exists(model_path):
    pass
else:
    err_msg = 'MODEL_PATH is either inaccessible or missing.  Please check the path in your .env and try again.'
    if (logging_mode):
        logging.error(err_msg)
    raise SystemExit(err_msg)

model_name = os.getenv('MODEL_NAME')

if model_name is None:
    err_msg = 'MODEL_NAME is missing.  Please check the name in your .env and try again.'
    if (logging_mode):
        logging.error(err_msg)
    raise SystemExit(err_msg)

gpt = GPT4All(model_name=model_name,
              model_path=model_path, allow_download=False)

operating_system = platform.system()

route = os.getenv('ROUTE')

if route is None:
    route = '/'


@app.route(route, methods=['POST'])
def generate():
    if request.json is None:
        err_msg = '[ERROR] No JSON data found in request.'
        if (logging_mode):
            logging.error(err_msg)
        raise SystemExit(err_msg)

    prompt = request.json.get('prompt')
    persona = request.json.get('persona')
    assist = request.json.get('assist')
    debug = request.json.get('debug')
    temperature = request.json.get('temp')

    if os.getenv('HEADER') == 'False':
        header = False
    elif os.getenv('HEADER') == 'True':
        header = True
    else:
        header = False
    if os.getenv('FOOTER') == 'False':
        footer = False
    elif os.getenv('FOOTER') == 'True':
        footer = True
    else:
        footer = False
    if os.getenv('STREAM') == 'False':
        stream = False
    elif os.getenv('STREAM') == 'True':
        stream = True
    else:
        stream = False

    if prompt is None:
        err_msg = '[ERROR] No prompt found in request.'
        if (logging_mode):
            logging.error(err_msg)
        raise SystemExit(err_msg)

    messages_info = []

    if prompt:
        messages_info.append({"role": "user", "content": str(prompt)})
    if persona:
        messages_info.append({"role": "system", "content": str(persona)})
    if assist:
        messages_info.append({"role": "assistant", "content": str(assist)})

    verbose_output = bool(debug) if debug else False
    stream_output = bool(stream) if stream else False

    if temperature is None:
        temperature = 0.9

    settings = {
        "n_predict": int(8192),
        "top_k": int(40),
        "top_p": float(.1),
        "temp": float(.9),
        "n_batch": int(16),
        "repeat_penalty": float(1.2),
        "repeat_last_n": int(64),
        "context_erase": float(.5),
        "streaming": stream_output
    }

    try:
        response = gpt.chat_completion(
            messages=messages_info,
            verbose=verbose_output,
            default_prompt_header=header,
            default_prompt_footer=footer,
            **settings
        )
        watchdog_file = os.getenv('WATCHDOG_TIMEFILE')
        if watchdog_file is None:
            watchdog_file = '.pywatchdog'
        logs_folder = os.getenv('LOGS_FOLDER')
        if logs_folder is None:
            logs_folder = 'logs'

        if os.path.exists(watchdog_file):
            try:
                os.remove(watchdog_file)
            except Exception as e:
                err_msg = f'[ERROR] Could not remove watchdog file: {e}]'
                if (logging_mode):
                    logging.error(err_msg)

        return response['choices'][0]['message']['content']

    except Exception as e:
        err_msg = str(e).encode("utf-8", errors="ignore").decode("utf-8")
        if logging_mode:
            logging.error(f'An error occurred: {err_msg}')
        return jsonify({'error': err_msg})


if __name__ == '__main__':

    db_path = os.getenv('MODEL_PATH')

    if db_path is not None and os.path.exists(db_path):
        pass
    else:
        err_msg = f'MODEL_PATH is either inaccessible or missing.  Please check the path in your .env and try again.'
        if logging_mode:
            logging.error(err_msg)
        raise SystemExit(err_msg)

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
    try:
        if debug_mode is False:
            with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
                app.run(debug=False, host=listen_host, port=listen_port)
        else:
            app.run(debug=True, host=listen_host, port=listen_port)
    except Exception as e:
        err_msg = str(e).encode("utf-8", errors="ignore").decode("utf-8")
        if logging_mode:
            logging.error(f'An error occurred: {err_msg}')
        raise SystemExit(f'An error occurred: {err_msg}')
