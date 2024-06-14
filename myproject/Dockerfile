# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install mysqlclient dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
