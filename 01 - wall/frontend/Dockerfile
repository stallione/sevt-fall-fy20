# Start from NGINX
FROM nginx:latest

# Set the working directory to /
WORKDIR /usr/share/nginx/html

# Copy required configuration files
ADD . /usr/share/nginx/html

# Install curl
RUN apt-get update && apt-get install -y curl

# Run it
CMD ./set_apiendpoint.sh && nginx -g 'daemon off;'

# Expose a port
EXPOSE 80
