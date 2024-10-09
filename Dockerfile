FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt .
COPY app.py .

RUN pip --no-cache-dir install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD ["./app.py", "--server.port=8501", "--server.address=0.0.0.0"]