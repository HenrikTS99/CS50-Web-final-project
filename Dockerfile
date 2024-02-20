FROM python:3.10
COPY . /src/app
WORKDIR /src/app
RUN pip install -r requirements.txt
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]