FROM python:3.10
WORKDIR /code
EXPOSE 3100
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./blog /code/blog
COPY ./chat /code/chat
COPY ./catchAllFunction /code/catchAllFunction
COPY ./host.json /code/host.json
COPY ./local.settings.json /code/local.settings.json

CMD ["uvicorn", "blog.app:app", "--host", "0.0.0.0", "--port", "3100", "--proxy-headers"]
