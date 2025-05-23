FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN  curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs


RUN pip install --upgrade pip    
COPY requirements.txt /app/


RUN pip install -r requirements.txt

COPY . /app


EXPOSE 80

CMD ["gunicorn", "employementProject.wsgi:application", "--bind", "0.0.0.0:8000"]
