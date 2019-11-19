# Use ubuntu-python3 plain image as base
FROM python:3

# Set the working directory to /
WORKDIR /

# Copy required configuration files
ADD requirements.txt /

# Optionally define proxy environment

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
