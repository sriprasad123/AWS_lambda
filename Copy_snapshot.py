import boto3

#client = boto3.client('sqs')
queue_url = 'https://sqs.us-east-2.amazonaws.com/498543524156/Queue_snapid'
dest_region=boto3.client('ec2', region_name='us-east-1')
sqs_client = boto3.client('sqs')
kms_key_id = "1657d948-6254-43e1-b3f1-bb834aa2bfa7"

def lambda_handler(event, context):
    messages = []
    
    queue_count = sqs_client.get_queue_attributes(QueueUrl=queue_url,AttributeNames=['All'])
    q= int(queue_count['Attributes']['ApproximateNumberOfMessages'])
    
    
    while True:
        resp = sqs_client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=10
        )

        try:
            messages.extend(resp['Messages'])
        except KeyError:
            break

        entries = [
            {'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']}
            for msg in resp['Messages']
        ]

    print(q)
    #return messages
    for i in range(q):
        response= messages[i]["Body"]
        print(messages[i])
        receipt_handle = messages[i]["ReceiptHandle"]
        print("index", i, "receipt handle", receipt_handle)
            
        copy_snap = dest_region.copy_snapshot(SourceRegion='us-east-2',
                                          SourceSnapshotId=response,
                                          Encrypted=True,
                                          KmsKeyId=kms_key_id,
                                          TagSpecifications=[
            {
                'ResourceType': 'snapshot',
                'Tags': [
                    {
                        'Key': 'nonroot',
                        'Value': 'yes'
                    },
                ]
            },
        ])
        queue_delete = sqs_client.delete_message_batch(
            QueueUrl=queue_url, Entries=entries
        )
		
