import os
import json
import requests
import sys
import time
import argparse

from flask import request,jsonify
from flask_restful import  Api,Resource

from app.common.error_handling import AppErrorBaseClass,ObjectNotFound

def sendRequest(url, data, apiKey = None):  
    json_data = json.dumps(data)
    
    if apiKey == None:
        response = requests.post(url, json_data)
    else:
        headers = {'X-Auth-Token': apiKey}
        response = requests.post(url, json_data, headers = headers)
    
    try:
      httpStatusCode = response.status_code 
      if response == None:
          print("No output from service")
          sys.exit()
      output = json.loads(response.text)	
      if output['errorCode'] != None:
          print(output['errorCode'], "- ", output['errorMessage'])
          sys.exit()
      if  httpStatusCode == 404:
          print("404 Not Found")
          sys.exit()
      elif httpStatusCode == 401: 
          print("401 Unauthorized")
          sys.exit()
      elif httpStatusCode == 400:
          print("Error Code", httpStatusCode)
          sys.exit()
    except Exception as e: 
          response.close()
          print(e)
          sys.exit()
    response.close()
    
    return output['data']

def setToken():
    username = os.getenv("USER_USGS")
    password = os.getenv("USER_PASS")
    serviceUrl = os.getenv("USGS_URL")

    # login
    payload = {'username' : username, 'password' : password}

    apiKey = sendRequest(f"{serviceUrl}/login", payload)
    os.environ["TOKEN"] = apiKey
    return (apiKey)

def getToken():
    token = os.getenv("TOKEN")
    if len(token) == 0:
        token = setToken()
    return token

def write_download(url,output):
    r = requests.get(url)
    with open(output, 'wb') as f:
        f.write(r.content)

class CatalogList(Resource):
    def post(self):
        data = request.get_json()
        token = getToken()
        serviceUrl = os.getenv("USGS_URL")
        acquisition_filter={
            "start":data["fecha_inicio"],
            "end":data["fecha_fin"]
        }
        cloud_filter = {
            "max":data["nubosidad_max"]
        }
        spatial_filter = {
            "filterType":"mbr",
            "lowerLeft":{
                "latitude":data["lat"],
                "longitude":data["lon"],
            },
            "upperRight":{
                "latitude":data["lat"],
                "longitude":data["lon"],
            }
        }
        scene_filter = {
            "acquisitionFilter":acquisition_filter,
            "cloudCoverFilter":cloud_filter,
            "spatialFilter":spatial_filter,
        }
        json_request = {
            "datasetName" : data["dataset"],
            "maxResults":1000,
            "sceneFilter":scene_filter
        }
        scenes = sendRequest(f"{serviceUrl}/scene-search",json_request, token)
        jsonSalida = {}
        jsonSalida["escenas_encontradas"] = len(scenes["results"]) 
        jsonSalida["escenas"] = []
        # Process the result 
        for scene in scenes["results"]: 
            jsonSalida["escenas"].append({ 
                "fecha":scene['publishDate'].split(" ")[0],
                "identificador":scene['displayId'],
                "entityId":scene['entityId']
            }) 
        return jsonSalida

class DownloadScene(Resource):
    def post(self):
        data = request.get_json()
        token = getToken()
        serviceUrl = os.getenv("USGS_URL")
        json_request = {
            'datasetName' : data['dataset'],
            "entityIds":data['escena']
        }
        downloadOptions = sendRequest(f"{serviceUrl}/download-options", json_request, token)
        downloads=[]
        for product in downloadOptions:
            if product['available'] == True and product["productName"] == "Level-1 GeoTIFF Data Product":
                downloads.append(
                    {'entityId' : product['entityId'],
                    'productId' : product['id']}
                )
        if downloads:
            os.makedirs(data["out_dir"], exist_ok=True)
            # create_folder(data["out_dir"])
            requestedDownloadsCount = len(downloads)
            label = "download-eos"
            payload = {'downloads' : downloads,'label' : label}
            requestResults = sendRequest(f"{serviceUrl}/download-request", payload, token)
            if requestResults['preparingDownloads'] != None and len(requestResults['preparingDownloads']) > 0:
                payload = {'label' : label}
                moreDownloadUrls = sendRequest(f"{serviceUrl}/download-retrieve", payload, token)
                downloadIds = []
                for download in moreDownloadUrls['available']:
                    downloadIds.append(download['downloadId'])
                    write_download(download['url'],data["out_dir"])
                    print("DOWNLOAD: " + download['url'])
                    
                for download in moreDownloadUrls['requested']:
                    downloadIds.append(download['downloadId'])
                    write_download(download['url'],data["out_dir"])
                    print("DOWNLOAD: " + download['url'])
                    
                # Didn't get all of the reuested downloads, call the download-retrieve method again probably after 30 seconds
                while len(downloadIds) < requestedDownloadsCount: 
                    preparingDownloads = requestedDownloadsCount - len(downloadIds)
                    print("\n", preparingDownloads, "downloads are not available. Waiting for 30 seconds.\n")
                    time.sleep(30)
                    print("Trying to retrieve data\n")
                    moreDownloadUrls = sendRequest(f"{serviceUrl}/download-retrieve", payload, token)
                    for download in moreDownloadUrls['available']:
                        if download['downloadId'] not in downloadIds:
                            downloadIds.append(download['downloadId'])
                            print("DOWNLOAD: " + download['url'])
                            write_download(download['url'],data["out_dir"])
            else:
                # Get all available downloads
                for download in requestResults['availableDownloads']:
                    # TODO :: Implement a downloading routine
                    print("DOWNLOAD: " + download['url'])
        else:
            raise ObjectNotFound('No se obtuvieron resultados para la consulta')
        return downloadIds