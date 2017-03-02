#!/usr/bin/env python

"""
Based on template-generating examples in troposphere repo.
"""

import configparser

from troposphere import Output, Ref, Template, constants, Parameter
from troposphere.elasticsearch import Domain, EBSOptions
from troposphere.elasticsearch import ElasticsearchClusterConfig
from troposphere.elasticsearch import SnapshotOptions
from troposphere.s3 import Bucket, PublicRead
import troposphere.ec2 as ec2


config = configparser.ConfigParser()
config.read('config.ini')

t = Template()
t.add_description('An S3 bucket and an ES domain')

# keypair for access
keypair = t.add_parameter(Parameter(
    "KeyPair",
    Type="String",
    Description="The name of the keypair to use for SSH access",
))

# Create a security group
sg = ec2.SecurityGroup('MySecurityGroup')
sg.GroupDescription = "Allow access to MyInstance"
sg.SecurityGroupIngress = [
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="22",
        ToPort="22",
        CidrIp="0.0.0.0/0",
    )]

# Add security group to template
t.add_resource(sg)

# S3 bucket
s3bucket = t.add_resource(Bucket("S3Bucket", AccessControl=PublicRead,))
o = Output("S3Bucket",
           Value=Ref(s3bucket),
           Description="File input bucket")
t.add_output(o)

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
es_domain = t.add_resource(domain)

print(t.to_json())
