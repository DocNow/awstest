#!/usr/bin/env python3

import configparser

from awacs import aws, sts
from troposphere import Output, Ref, Template
from troposphere.s3 import Bucket, PublicRead


docnow_template = Template()

docnow_template.add_description("Cloudformation S3")

docnows3bucket = docnow_template.add_resource(Bucket("S3Bucket",
    AccessControl=PublicRead,))

docnow_template.add_output(Output("BucketName", Value=Ref(docnows3bucket),
    Description="Docnow s3 Bucket to host json files"))

print(docnow_template.to_json())
