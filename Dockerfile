
FROM python:3.9
RUN useradd --system youmu -U
WORKDIR /youmu
RUN chown youmu:youmu -R /youmu
USER youmu
RUN python -m venv .venv
COPY requirements.txt .
RUN . .venv/bin/activate && python -m pip install -r requirements.txt
COPY . .
CMD . .venv/bin/activate && exec python main.py
