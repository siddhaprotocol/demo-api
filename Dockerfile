FROM python:3.12.3

WORKDIR /code

# Install necessary packages
RUN apt-get update && \
    apt-get upgrade -y

# Copy and install requirements
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /code/app

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]