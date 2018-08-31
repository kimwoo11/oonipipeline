#!/usr/bin/env python

import boto3  # Accessing S3 bucket
import botocore  # Accessing S3 bucket
import os
from botocore.handlers import disable_signing


class OoniDataGrabber:

    s3_ooni_bucket_name = "ooni-data"  # S3 Bucket Name for OONI Data
    s3_ooni_base_dir = "autoclaved/jsonl/"  # S3 Prefix directory for OONI Data
    s3_is_anonymous = True  # S3 flag for signing/not signing requests

    def __init__(self):
        self.s3 = boto3.resource('s3')  # For downloading files from the S3 Bucket
        if self.s3_is_anonymous:
            # Use anonymous clients for resources
            self.s3.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
        self.s3bucket = self.s3.Bucket(self.s3_ooni_bucket_name)

    def download_s3_file(self, s3_key, output_filename=""):
        """
        Given an s3 path as str download that into output_filename from OONI bucket
        :param s3_key: Your S3 key as a string
        :param output_filename: your filename otherwise the s3 filename is used
        :return: downloaded file into local directory
        """
        if output_filename == "":
            output_filename = os.path.basename(s3_key)

        s3_key = self.s3_ooni_base_dir + s3_key

        try:
            self.s3bucket.download_file(s3_key, output_filename)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
