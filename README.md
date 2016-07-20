# Migrate from private docker registry to gcloud

### Description
Written in Python:
Running `python migrate.py` will get a list of all available repositories and version tags from your existing private registry and will push all new repos with images/versions to your Gcloud docker registry

### Requirements
Gcloud sdk must be installed and authenticated.
Gcloud alpha command group needs to be installed.

You must have a project created with gcloud.

Private registry you are migrating from should have HTTPS enabled.


Four Environment Variables need to be exported
```
export GCLOUD_URL="gcr.io/<project-name>"
export REG_URL="docker-registry.example.com:5000"
export GCLOUDPATH = "/usr/bin/gcloud"
export DOCKERPATH = "/usr/bin/docker"
```

### GCloud SDK install
[Link to interactive install](https://cloud.google.com/sdk/downloads#interactive)


### Troubleshooting

If you see something like the following: You are missing an exported variable.

```
Traceback (most recent call last):
  File "./migrate.py", line 122, in <module>
    MigrateToGcloud()
  File "./migrate.py", line 36, in __init__
    self._get_catalog()
  File "./migrate.py", line 40, in _get_catalog
    r = requests.get('https://' + self.REG_URL + 'v2/_catalog')
```
