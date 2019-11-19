# Use ubuntu-python-3 appd image
FROM 10.139.12.200/cl-wall/ubuntu-python3-appd

# Set the working directory to /
WORKDIR /

# Copy required configuration files
ADD event_fetch.py appd_config_gen.py /

# Optionally define proxy environment
# ARG http_proxy=http://proxy-wsa.esl.cisco.com:80
# ARG https_proxy=http://proxy-wsa.esl.cisco.com:80

# Run it
CMD python appd_config_gen.py && pyagent run -c /appdynamics.cfg -- python /event_fetch.py
