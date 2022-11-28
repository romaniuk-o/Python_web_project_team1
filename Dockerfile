FROM python:3.10

WORKDIR /Python_web_project_team1

COPY . /Python_web_project_team1

RUN pip install -r requirements.txt

CMD ["python", "app.py"]