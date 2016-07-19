# Migrate from private docker registry to gcloud

### Description
Running `python migrate.py` will get a list of all available repositories and version tags from your existing private registry and will push all new repos with images/versions to your Gcloud docker registry

### Requirements
Gcloud sdk must be installed and authenticated
You must have a project created with gcloud
Private registry you are migrating from should have HTTPS enabled.


Four Environment Variables need to be exported
```
export GCLOUD_URL="gcr.io/<project-name>/"
export REG_URL="docker-registry.example.com:5000/"
export GCLOUDPATH = "/usr/bin/gcloud"
export DOCKERPATH = "/usr/bin/docker"
```
