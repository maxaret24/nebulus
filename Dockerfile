FROM python:3.10-bullseye
RUN apt-get update && apt-get install -y ffmpeg neofetch curl wget git wkhtmltopdf
WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3","-m","ub"]