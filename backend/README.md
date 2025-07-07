# Kitchen

`kitchen` is the Python-based backend for the restaurant application.


## Running

Create a virtual machine (optional but recommended):
```bash
python3 -m venv venv
```

Install the dependencies:
```bash
pip3 install -r requirements.txt
```

Setup the environment variables:
```bash
cp .env.example .env
vim .env # fill in the missing environment vars
```

Run the server:
```bash
python3 kitchen/main.py
```

Run all unit tests:
```bash
python3 -m unittest discover kitchen
```

