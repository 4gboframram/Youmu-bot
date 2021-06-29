
FROM python:3.9
WORKDIR /usr/src/youmu
VOLUME /usr/src/youmu/data
COPY requirements.txt .
RUN python -m pip install -U pip && python -m pip install -U wheel && python -m pip install -r requirements.txt
COPY . .
CMD python main.py
