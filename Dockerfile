FROM python:3.10
LABEL authors="daeneys"

COPY . /app
WORKDIR /app

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080/tcp

ENTRYPOINT ["python", "main.py"]
