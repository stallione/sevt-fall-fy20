# The Cisco Live Wall!
##### A simple microservices application that provides information on the weather, events and incident issues in the Barcelona area.
<hr>
Note: This uses an external MySQL database to store data.<b> It also assumes you are in a Cisco Lab, therefore you use a proxy. Current implementation does not allow for direct internet connection.
You are required to create this database and inject the mysqldump.sql script to create the database, the user and required tables. Ensure the password configured in the sql script and the ones referenced in the YAMLs or Cloudcenter Services are the same.</b>

#### Deployment methods
This application can be deployed in two ways:
* From Kubernetes directly
* Using Cisco Cloudcenter

#### Prerequisites
To make this application work, you will need to obtain a valid API key for three services:
* Openweathermap
* Eventbrite
* Bing maps

Use the following links to create your own API key:
###### Openweathermap
https://openweathermap.org/api
###### Evenbrite
https://www.eventbrite.com/platform/
###### BING Maps
https://docs.microsoft.com/en-us/bingmaps/getting-started/bing-maps-dev-center-help/getting-a-bing-maps-key

#### Building
##### Build the base image
Move to the directory "Dockerfiles/ubuntu-python3-appd", check the dockerfile and change the proxy or remove it for good.
Build the image with:

`docker build . -t ubuntu-python3-appd` 

Tag and push your image in your favourite registry. 

##### Build the service images
Under each service directory (frontend, apiserver, weather, event, incident), modify the Dockerfile to point to the just created base image.
Build the image with:

`docker build . -t the_service_name`

Tag and push your image in your favourite registry.

#### Configuration
- Clone the repository, then move to the yaml directory
- Identify a valid, reachable docker registry
- (Native Kubernetes deployment) Edit the deployment yamls to reflect your configuration (usernames, passwords, apikeys, registry, etc.)
- (Cisco Cloudcenter deployment) Edit your services to reflect your configuration (usernames, passwords, apikeys, registry, etc.)


#### Deploy

##### Option 1. Kubernetes
Execute the following script:

`./launch-livewall.sh`

To destroy the deployment:

`./destroy_livewall.sh`

##### Option 2. Cisco Cloudcenter
- Download the application profile from the cloudcenter directory
- In cloudcenter create the required services. As of today, services cannot be exported so you will have to create them. You can refer to the yamls to identify the right values  
- In Cloudcenter, import the application profile. <b>Note: you have to create the services in advance. Check your application profile before deploy, you will have to have a match on the services, images and network services
- Deploy the Application Profile
EOM
