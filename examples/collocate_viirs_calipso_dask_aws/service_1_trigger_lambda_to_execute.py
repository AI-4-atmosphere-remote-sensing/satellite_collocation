import json, boto3, time, sys, os

credentials = ["us-west-2","your-access-key","your-secret-key"]   #region,access_key,secret_key
InstanceId = 'i-0b83239ada0a8ae1d' ## change to your EC2 instance ID

def get_ec2_instances_id(region,access_key,secret_key):
    ec2_conn = boto3.resource('ec2',region_name=region,aws_access_key_id=access_key,aws_secret_access_key=secret_key)
    
    if ec2_conn:
        for instance in ec2_conn.instances.all():
            if instance.state['Name'] == 'running' and instance.security_groups[0]['GroupName'] == 'launch-wizard-13':
                masterInstanceId = instance.instance_id
                print("Master Instance Id is ",masterInstanceId)
        return masterInstanceId
    else:
        print('Region failed', region)
        return None

def send_command_to_master(InstanceId,command,ssm_client):
    response = ssm_client.send_command(InstanceIds=[InstanceId],DocumentName="AWS-RunShellScript",Parameters={'commands': [command]})
    cmdId = response['Command']['CommandId']
    return cmdId
    
def lambda_handler(event, context):
    masterInstanceId = InstanceId 
    ssm_client = boto3.client('ssm',region_name=credentials[0],aws_access_key_id=credentials[1],aws_secret_access_key=credentials[2])
    return send_command_to_master(masterInstanceId,\
        "cd /home/ubuntu/satellite_collocation-main && /usr/bin/python3 examples/collocate_viirs_calipso_dask_cluster/collocation_dask_local.py -tp ../satellite_collocation_sample_data/CALIPSO-L2-01km-CLayer/ -sgp ../satellite_collocation_sample_data/VNP03MOD-VIIRS-Coordinates/ -sdp ../satellite_collocation_sample_data/VNP02MOD-VIIRS-Attributes/ -sp ../satellite_collocation_sample_data/collocation-output/",\
        ssm_client)
