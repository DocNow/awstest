#!/usr/bin/env python3

import configparser

from awacs import aws, sts
from troposphere import Output, Ref, Template, constants
from troposphere.s3 import Bucket, PublicRead
from troposphere.elasticsearch import Domain, EBSOptions
from troposphere.elasticsearch import ElasticsearchClusterConfig
from troposphere.elasticsearch import SnapshotOptions
from troposphere.iam import Role, InstanceProfile

import Allow, Statement, Principal, Policy
import AssumeRole

config = configparser.ConfigParser()
config.read('config.ini')

docnow_template = Template()

docnow_template.add_description("Cloudformation for S3, elasticsearch")

# S3 bucket
docnows3bucket = docnow_template.add_resource(Bucket("S3Bucket",
    AccessControl=PublicRead,))

docnow_template.add_output(Output("BucketName", Value=Ref(docnows3bucket),
    Description="Docnow s3 Bucket to host json files"))

# ES domain
config_es = config['elasticsearch']
es_cluster_config = ElasticsearchClusterConfig(
    DedicatedMasterEnabled=config_es.getboolean('DedicatedMasterEnabled'),
    DedicatedMasterCount=config_es.getint('DedicatedMasterCount'),
    InstanceCount=config_es.getint('InstanceCount'),
    InstanceType=constants.ELASTICSEARCH_M3_MEDIUM,
    DedicatedMasterType=constants.ELASTICSEARCH_M3_MEDIUM,
    ZoneAwarenessEnabled=config_es.getboolean('ZoneAwarenessEnabled')
    )
ebs_options = EBSOptions(EBSEnabled=True,
                         Iops=0,
                         VolumeSize=20,
                         VolumeType="gp2"
                         )
domain = Domain(
    'ElasticsearchDomain',
    DomainName='testelasticsearchdomain',
    ElasticsearchVersion='5.1',
    ElasticsearchClusterConfig=es_cluster_config,
    EBSOptions=ebs_options,
    SnapshotOptions=SnapshotOptions(AutomatedSnapshotStartHour=0),
    AccessPolicies={'Version': '2012-10-17',
                    'Statement': [{
                        'Effect': 'Allow',
                        'Principal': {
                            'AWS': '*'
                        },
                        'Action': 'es:*',
                        'Resource': '*'
                    }]},
    AdvancedOptions={"rest.action.multi.allow_explicit_index": "true"}
    )
es_domain = docnow_template.add_resource(domain)

docnowlambdaRole = docnow_template(Role(
    "DocnowLambaRole",
    AssumeRolePolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[AssumeRole],
                Principal=Principal("Service", ["lambda.amazonaws.com"]
            )
        ]
    )
))


print(docnow_template.to_json())
