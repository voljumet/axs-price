# Use an official lightweight Python image
FROM python:3.8-slim-buster

# Set the working directory in docker
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the files to the working directory
COPY axs.py ./
COPY price.py ./
COPY templates/index.html ./templates/index.html

# Specify the command to run on container start
CMD ["python", "./price.py"]
