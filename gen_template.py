#!/usr/bin/env python

"""
Based on template-generating examples in troposphere repo.
"""

from troposphere import Output, Ref, Template, constants
from troposphere.elasticsearch import Domain, EBSOptions
from troposphere.elasticsearch import ElasticsearchClusterConfig
from troposphere.elasticsearch import SnapshotOptions
from troposphere.s3 import Bucket, PublicRead


t = Template()
t.add_description('An S3 bucket and an ES domain')

# S3 bucket
s3bucket = t.add_resource(Bucket("S3Bucket", AccessControl=PublicRead,))
o = Output("S3Bucket",
           Value=Ref(s3bucket),
           Description="File input bucket")
t.add_output(o)

# ES domain
es_cluster_config = ElasticsearchClusterConfig(
    DedicatedMasterEnabled=True,
    InstanceCount=2,
    ZoneAwarenessEnabled=True,
    InstanceType=constants.ELASTICSEARCH_M3_MEDIUM,
    DedicatedMasterType=constants.ELASTICSEARCH_M3_MEDIUM,
    DedicatedMasterCount=2
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
