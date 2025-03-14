FROM ubuntu:noble

WORKDIR /app

COPY requirements.txt .

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y python3 python3-pip python3.12-venv

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install --no-cache-dir -r requirements.txt

RUN playwright install && playwright install-deps

COPY bin-canary /app

CMD python app.py
