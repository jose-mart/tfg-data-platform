import logging

import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

import requests
from datetime import datetime
import json
import xmltodict
import gzip

import os
from io import BytesIO, StringIO


def main(
    mytimer: func.TimerRequest,
    log: func.Out[str]) -> None:
    
    # variables
    connect_str = os.environ['AzureWebJobsStorage']
    sensor_data_url = os.environ['sensor_data_url']
    sensor_description_url = os.environ['sensor_description_url']

    logging.info('Setting up date.')
    utc_timestamp = datetime.now()

    year = utc_timestamp.strftime("%Y")
    month = utc_timestamp.strftime("%m")
    day = utc_timestamp.strftime("%d")
    hour = utc_timestamp.strftime("%H")
    minute = utc_timestamp.strftime("%M")
    dataset = None
    path = None

    # Setting up credentials
    sbc = BlobServiceClient.from_connection_string(connect_str) 
    stdin = None

    # Request sensor_data
    logging.info('Start sensor data retrieving.')
    sensor_data_request = False
    try:
        logging.info('Retrieving sensor data.')
        r = requests.get(sensor_data_url)
        logging.info('Requests succesful. Checking status code.')
        sensor_data_request = True if r.status_code == 200 else False
        logging.info(f'Status code {r.status_code}.')
    
        # Save to datalake
        logging.info(f'Saving data sensor to datalake.')
        dataset = "sensor_data"
        path = f"raw/{dataset}/{year}/{month}/{day}/{hour}/{dataset}_{year}{month}{day}{hour}{minute}.json.gz"
        
        logging.info(f'Getting blob client.')
        bc = sbc.get_blob_client(container = "datalake", blob=path)

        # Converting from XML to json
        stdin = StringIO(r.text)
        json_file = json.dumps(xmltodict.parse(stdin.read()))

        # Compressing data
        encoded = json_file.encode('utf-8')

        # Writing blob
        logging.info(f'Uploading blob client.')
        bc.upload_blob(gzip.compress(encoded), blob_type = "BlockBlob")
        logging.info('Sensor data saved.')
    except:
        logging.info('Something has gone wrong.')
        sensor_data_request = False

    # Request sensor_description
    logging.info('Start sensor description retrieving.')
    sensor_description_request = False
    try:
        logging.info('Retrieving sensor description.')
        r = requests.get(sensor_description_url)
        logging.info('Requests succesful. Checking status code.')
        sensor_description_request = True if r.status_code == 200 else False
        logging.info(f'Status code {r.status_code}.')

        # Save to datalake
        logging.info(f'Saving data sensor to datalake.')
        dataset = "sensor_description"
        path = f"raw/{dataset}/{year}/{month}/{day}/{hour}/{dataset}_{year}{month}{day}{hour}{minute}.json.gz"
        
        logging.info(f'Getting blob client.')
        bc = sbc.get_blob_client(container = "datalake", blob=path)

       # Converting from XML to json
        stdin = StringIO(r.text)
        json_file = json.dumps(xmltodict.parse(stdin.read()))

        # Compressing data
        encoded = json_file.encode('utf-8')

        # Writing blob
        logging.info(f'Uploading blob client.')
        bc.upload_blob(gzip.compress(encoded), blob_type = "BlockBlob")
        logging.info('Sensor data saved.')
    except:
        logging.info('Something has gone wrong.')
        sensor_description_request = False

    # Log sensor_description into log table
    sensor_description_log ={
        "PartitionKey": "sensor_description",
        "RowKey": utc_timestamp.strftime("%Y%m%d%H%M"),
        "date": utc_timestamp.isoformat(),
        "path": path,
        "status": "Succesful" if sensor_description_request else "Failed"
    }

    # Log sensor_data trace into log table
    sensor_data_log ={
        "PartitionKey": "sensor_data",
        "RowKey": utc_timestamp.strftime("%Y%m%d%H%M"),
        "date": utc_timestamp.isoformat(),
        "path": path,
        "status": "Succesful" if sensor_data_request else "Failed"
    }
    
    log.set(json.dumps([sensor_data_log, sensor_description_log]))
    logging.info('Log saved.')
