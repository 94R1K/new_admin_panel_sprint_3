FROM python:3.11-bullseye

WORKDIR /etl

COPY ./etl/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "load_data.py"]