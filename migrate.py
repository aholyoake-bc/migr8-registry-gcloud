#!/usr/bin/env python3
# Must have python installed with requestite libs
# This script assumes you have gcloud sdk installed and
# the sdk has already be authenticated to gcloud
# It also assumes access to your private repository through the REG_URL

import requests
import pickle
from requests.auth import HTTPBasicAuth
import json
import logging
import ast
import sys
import subprocess
from multiprocessing import Pool
import os
import tqdm

os.path.abspath('/')

logger = logging.getLogger('migrate')
logger.setLevel(logging.DEBUG)
##########################################
#  Examples for GCLOUD_URL AND REG_URL
# export GCLOUD_URL="gcr.io/<project-name>"
# export REG_URL="docker-registry.example.com:5000"
# export REG_PROTOCOL="https://"
# export GCLOUDPATH="/usr/bin/gcloud"
# export DOCKERPATH="/usr/bin/docker"
# Make sure you have these env vars set
os.environ.get('GCLOUD_URL')
os.environ.get('REG_URL')
os.environ.get('GCLOUDPATH')
os.environ.get('DOCKERPATH')
os.environ.get('DOCKERUSER')
os.environ.get('DOCKERPASSWORD')


def upload(repo):
    ip = ImageProcessor(repo[0],repo[1])
    ip.do()

class ImageProcessor:

    def __init__(self,repo,tag):
        self.REG_URL = os.environ.get('REG_URL')
        self.REG_PROTOCOL = os.environ.get('REG_PROTOCOL')
        self.GCLOUD_URL = os.environ.get('GCLOUD_URL')
        self.dockerpath = os.environ.get('DOCKERPATH')
        self.gcloudpath = os.environ.get('GCLOUDPATH')
        self.repo = repo
        self.tag = tag

    def do(self):
        self.download_images()
        self.set_tag()
        self.upload_image()


    def download_images(self):
        try:
            command = (self.dockerpath + ' pull ' +
                       self.REG_URL + '/' + self.repo + ':' + self.tag)
            subprocess.check_output(command, shell=True, executable='/bin/bash')
        except:
            return

    def set_tag(self):
        try:
            command = ('docker tag ' + self.REG_URL + '/' + self.repo +
                       ':' + self.tag + ' ' + self.GCLOUD_URL + '/' + self.repo + ':' + self.tag)
            subprocess.check_output(command, shell=True, executable='/bin/bash')
        except:
            return

    def upload_image(self):
        try:
            command = ('docker push ' +
                       self.GCLOUD_URL + '/' + self.repo + ':' + self.tag)
            subprocess.check_output(command, shell=True, executable='/bin/bash')

        except:
            return


class MigrateToGcloud:
    # Init some urls and paths for migration then call _get_catalog
    def __init__(self):
        self.REG_URL = os.environ.get('REG_URL')
        self.REG_PROTOCOL = os.environ.get('REG_PROTOCOL')
        self.GCLOUD_URL = os.environ.get('GCLOUD_URL')
        self.dockerpath = os.environ.get('DOCKERPATH')
        self.gcloudpath = os.environ.get('GCLOUDPATH')
        repositories = self.catalog()
        all_tags = {r: self.filter_tags(r,self.tags(r)) for r in repositories}
        # try:
        #        f = open("repo.pickle",'rb')
        #            # Do something with the file
        #        all_tags = pickle.load(f)
        #except IOError:
        #        print("File not accessible")
        #        repositories = self.catalog()
        #        all_tags = {r: self.filter_tags(r,self.tags(r)) for r in repositories}
        #        f = open("repo.pickle",'wb')
        #        pickle.dump(all_tags,f)

        #finally:
        #        f.close()


        for r,v in all_tags.items():
            print("{:40}: {}".format(r, len(v)))
    
        plist = [(r,t) for r,tt in all_tags.items() for t in tt]

        with Pool(24) as p:
            list(tqdm.tqdm(p.imap(upload, plist), total=len(plist)))

    def paginate(self,url):
        pagesize = 100
        link = True
        page_url = url + '?n={}'.format(n)

        pages = []
        while page_url:
            print(page_url)
            r = self.request(page_url)
            page_url = r.links.get("next")
            pages.append(r.json)

    def request(self,uri):
        return requests.get(uri)


    # Get a catalog of repos from your existing repository
    def catalog(self):
        r = self.paginate(self.REG_PROTOCOL + self.REG_URL + '/v2/_catalog')
        return [rr for a in r for rr in r['repositories']]
        
    def existing_tags(self, repo):
        command = self.gcloudpath + ' container images list-tags --format=json ' + self.GCLOUD_URL + '/' + repo
        checktags = subprocess.check_output(command, shell=True, executable='/bin/bash').decode()
        return [t for tags in json.loads(checktags) for t in tags['tags']]

    def filter_tags(self, repo, tags):
        existing_tags = self.existing_tags(repo)
        return [t for t in tags if t not in existing_tags]

    def tags(self, repo):
        print('Fetching tags for {}'.format(repo))
        command = self.REG_PROTOCOL + self.REG_URL + '/v2/' + repo + '/tags/list'
        r = self.paginate(command)
        return [rr for a in r for rr in r['tags']]


    def clean_up(self):
        try:
           subprocess.check_output('docker system prune -f', shell=True, executable='/bin/bash')
        except:
           return





MigrateToGcloud()
