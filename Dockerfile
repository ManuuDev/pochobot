FROM python:3

LABEL version="0.1"

LABEL description="Custom docker image for pochobot"

WORKDIR /app

COPY . /app

RUN echo "Installing ffmpeg"

RUN apt update

RUN apt install -y ffmpeg

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./Main.py" ]