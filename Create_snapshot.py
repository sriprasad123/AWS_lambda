import boto3
import os
import time
import json

ec = boto3.client('ec2', region_name='us-east-2')
ec2_vol = boto3.resource('ec2', region_name='us-east-2')
lam = boto3.client('lambda')
ec2resource = boto3.resource('ec2', 'us-east-2')
dest_region=boto3.client('ec2', region_name='us-east-1')
sqs = boto3.resource('sqs')
queue_url = 'https://sqs.us-east-2.amazonaws.com/498543524156/Queue_snapid'

def lambda_handler(event, context):
    #snapdate = snap['StartTime'].strftime('%m/%d/%Y')
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['backup', 'Backup']},
        ]
    ).get(
        'Reservations', []
    )

    #volumes = ec2_vol.volumes.filter(Filters=[{'Name': 'nonroot', 'Values': ['yes']}])
    resp_vol = ec.describe_volumes(Filters=[{
            'Name': 'tag-key','Values': ['nonroot']}])
    #print(resp_vol["Volumes"][0]["VolumeId"])
    data= resp_vol["Volumes"]
    for vol in data:
        print(vol["VolumeId"])
    
'''
    #to list the Volumes
    instances = sum([
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print ("Found %d instances that need backing up" % len(instances))
    print(instances)

    for instance in resp_vol:
        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            print ("Found EBS volume %s on instance %s" % (
                vol_id, instance['InstanceId']))
            print("Volume id"+vol_id)
        
        snap=ec.create_snapshot(VolumeId=vol_id, TagSpecifications=[
        {
            'ResourceType': 'snapshot',
            'Tags': [
                {
                    'Key': 'nonroot1',
                    'Value': 'yes'
                },
            ]
        },
    ])
        print("creating snapshot1" )
        snap_id = snap["SnapshotId"]
        print(snap_id)
        
        #creating and sending message to SQS
        queue = sqs.get_queue_by_name(QueueName='Queue_snapid')
        resp_queue=queue.send_message(MessageBody=snap_id)
        
        
        snapshot = ec2resource.Snapshot(snap['SnapshotId'])
        sn1=snapshot.create_tags(Tags=[{'Key': 'Name', 'Value': 'backup_test'}])
        #print(sn1)
        

        if not snapshot: 
            print("failure message")
            Send_Unsuccessful_Backup_Email()
        else:
            print("success message")  
            Send_Success_Email()
            
        return snap_id

    

def Send_Success_Email():

    SUBJECT = "[AWS Ohio]: Successfully performed EC2 Volume Backup"
    BODY_TEXT = ("Successfully provisioned snapshot backups")

    try:
        sns = boto3.client('sns')
        response = sns.publish(
                    TargetArn= 'arn:aws:sns:us-east-2:498543524156:my_topic',
                    Message= BODY_TEXT,
                    MessageStructure='string',
                    Subject= SUBJECT)
        print("Success Email Sent!")
    except Exception as e:
        print("Exception: %s" % str(e))
        
def Send_Unsuccessful_Backup_Email():

    SUBJECT = "[AWS Ohio]: EC2 Volume Backup is unsuccessful"
    BODY_TEXT = ("Root backup was completed but we encountered some errors during the process on %s or %s. Please check the logs for the error(s)." )

    try:
        sns = boto3.client('sns')
        response = sns.publish(
                    TopicArn='arn:aws:sns:us-east-2:498543524156:EBS-On-Failure',
                    Message= BODY_TEXT,
                    MessageStructure='string',
                    Subject= SUBJECT)
        print("Success Email Sent!")
    except Exception as e:
        print("Exception: %s" % str(e))
'''
