# GPT4All API Server with Watchdog

by [ClarkTribeGames, LLC](https://www.clarktribegames.com)

The `GPT4All API Server with Watchdog` is a simple HTTP server that monitors and restarts a Python application, in this case the server.py, which serves as an interface to [GPT4All compatible models](https://docs.gpt4all.io/gpt4all_faq.html).

## Features

- `Watchdog` Continuously runs and restarts a Python application.
- `Watchdog` Checks on application status and handles certain contingencies.
- `GPT4All API` Interfaces with GPT4All compatible models with API request and sends responses back from the model

## Prerequisites

- Windows , macOS, or Linux machine with Python 3.8 or later.
- Local Administrator / sudo access on the operating system.
- Appropriate firewall configuration (e.g. port forwarding) if taking external request [Not Recommended]

## Setup

Windows: Clone in a location that your user (or service account if using one) has full read/write access to.

macOS/Linux: We recommend cloning this repository into `/usr/local/bin` if you plan to use this as a service. You can, however, clone and run it from anywhere. Run these commands in your terminal:

```bash
cd /path-to-wherever/
git clone https://github.com/AznIronMan/gpt4all_api.git
```

We also recommend running this within a virtual Python environment:

NOTE: You can use Anaconda as well. It is not recommended not use a virtual Python environment.

```bash
# Windows
cd gpt4all_api
python.exe -m venv .venv
call .venv/Scripts/activate
```

```bash
# macOS/Linux
cd gpt4all_api
python3 -m venv .venv
source .venv/bin/activate
```

Be sure to install the pip requirements (confirm you are in your new `.venv` venv before doing so!)

```bash
pip install -r requirements.txt
```

Be sure to configure the `.env` file before starting! (Clone the .env.example and rename it .env and upload it with the appropriate information).

GGML models are recommended for this application. [GGML models on Hugging Face](https://huggingface.co/models?search=ggml)

NOTE: This application was only tested with WizardML GGML (non-falcon) models.

From there, to run the server, you can either:

```bash
# Windows
python.exe watchdog.py
```

```bash
# mac/OS/Linux
sudo python3 watchdog.py
```

Or you can use the bundled `start.bat` (Windows) or `start.sh` (macOS/Linux) included to start the server.

macOS/Linux users - You may need to run this command before to allow the `start.sh` to run on your OS:

```bash
sudo chmod +x ./start.sh
```

## Usage

# Watchdog

The `watchdog` portion of this application runs on your machine and monitors the `gpt4all_api` application. It checks for the existence of a `watchdog` file which serves as a signal to indicate when the `gpt4all_api` server has completed processing a request.

After each request is completed, the `gpt4all_api` server is restarted. This is done to reset the state of the `gpt4all_api` server and ensure that it's ready to handle the next incoming request. (This is to ensure fresh responses from the model. Trials showed that not restarting the api server resulted in repetitive and, sometimes, hallunication answers from different models.)

The `watchdog` checks if the `watchdog` file is missing for more than 5 seconds. The `gpt4all_api` server will remove the `watchdog` file upon completion, triggering the restart. If the `watchdog` file is missing the `gpt4all_api` responds to the request and/or if there is an error during the `gpt4all_api` process, the `watchdog` script assumes that something went wrong and attempts to restart the `gpt4all_api` server after logging the error into the `logs` folder.

# Gpt4all_api

The `gpt4all_api` server uses Flask to accept incoming API request. The default `route` is `/gpt4all_api` but you can set it, along with pretty much everything else, in the `.env`. You can send POST requests with a query parameter type to fetch the desired messages. Here are some examples of how to fetch all messages:

```bash
# Using curl:
curl -X POST http://serverhostname_or_ipaddress_here:5000/gpt4all_api -H "Content-Type: application/json" -d "{\"prompt\": \"your question or request goes here\", \"persona\": \"[your system prompt goes here]\"}"
```

```bash
# Using Postman:

Set the request type to POST.
Set the URL to http://serverhostname_or_ipaddress_here:5000/messages.
Under Params, add a key-value pair with
    key: 'prompt'
    value: 'your question or request goes here'
And
    key: 'persona'
    value: '[your system prompt goes here]'
```

## Detailed Setup

If you have trouble with the setup, you can follow these steps:

```bash
# macOS/Linux
cp .env.example .env
nano .env # or use TextEdit, VIM, VS Code, etc.
touch requirements.txt
nano requirements.txt
```

```bash
# Windows
copy .env.example .env
notepad .env # notepad is on everyone windows machine but vscode or notepad++ is recommended

(make edits to your .env)

# if you do not have a requirements.txt for some reason
notepad requirements.txt
```

Paste these contents into your `requirements.txt` file:

```makefile
blinker==1.6.2
certifi==2023.5.7
charset-normalizer==3.1.0
click==8.1.3
colorama==0.4.6
Flask==2.3.2
gpt4all==0.3.5
idna==3.4
itsdangerous==2.1.2
Jinja2==3.1.2
MarkupSafe==2.1.3
python-dotenv==1.0.0
requests==2.31.0
tqdm==4.65.0
urllib3==2.0.3
Werkzeug==2.3.6
```

Then install the requirements:

```bash
pip install -r requirements.txt
```

You can then use `python3 start.sh` (macOS/Linux) or `python.exe start.bat` (Windows) to start the server.

If you have any issues with the setup, please feel free to contact us using the details provided below.

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

## Contact

Discord: `AznIronMan`
E-Mail: **geoff** `at` **clark tribe games** `dot` **com** (_no spaces and replace at with @ and dot with ._)
