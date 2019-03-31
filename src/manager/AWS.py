import boto3
import os
from time import sleep

KEYNAME = 'saas-bot'
SECURITYGROUPS = ['saas-bot']
IMAGE_ID = os.environ.get('IMAGE_ID')


class AWS:
    def __init__(self, logger):
        self.logger = logger
        self.ec2 = boto3.resource('ec2', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                  aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        self.client = boto3.client('ec2', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                                   aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

    def start(self, user):
        not_terminated_instances = list(filter(lambda i: i.state['Name'] != 'terminated', self.get_user_instance_list(user=user)))
        if len(not_terminated_instances) >= 1:
            instance = not_terminated_instances[0]
            instance.start()
            self.logger.warning("for User %s start old Instance: %s" % (user, instance))

        else:
            instance = self.ec2.create_instances(
                ImageId=IMAGE_ID, InstanceType='t2.micro',
                KeyName=KEYNAME, SecurityGroups=SECURITYGROUPS,
                MaxCount=1, MinCount=1,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': user
                            },
                        ]
                    },
                ],
            )[0]
            self.logger.warning("for User %s start new Instance: %s" % (user, instance))

        return self.wait_for_instance(instance).public_ip_address

    def restart(self, user):
        not_terminated_instances = list(filter(lambda i: i.state['Name'] != 'terminated', self.get_user_instance_list(user=user)))
        if len(not_terminated_instances) >= 1:
            instance = not_terminated_instances[0]
            instance.reboot()
            self.logger.warning("for User %s ReStart old Instance: %s" % (user, instance))
            return self.wait_for_instance(instance).public_ip_address
        else:
            self.logger.warning("No Instance found for User: %s" % user)
            raise Exception("No Instance found for User: %s" % user)

    def stop(self, user):
        not_terminated_instances = list(
            filter(lambda i: i.state['Name'] != 'terminated', self.get_user_instance_list(user=user)))
        for instance in not_terminated_instances:
            instance.stop()

    def wait_for_instance(self, instance):
        while not instance.public_ip_address:
            sleep(10)
            self.logger.warning("wait for public_ip_address: %s" % instance)
            instance = self.ec2.Instance(instance.id)

        while instance.state['Name'] == 'pending':
            sleep(10)
            self.logger.warning("wait while pending %s" % instance)
            instance = self.ec2.Instance(instance.id)

        return instance

    def get_ip(self, user):
        instance_list = list(filter(lambda i: (i.state['Name'] == 'pending' or i.state['Name'] == 'running'),
                               self.get_user_instance_list(user=user)))
        if len(instance_list) <= 0:
            return None
        return instance_list[0].public_ip_address

    def get_user_instance_list(self, user):
        d = {'Key': 'Name', 'Value': user}
        return list(filter(lambda i: d in i.tags, self.get_instances()))

    def get_instances(self):
        response = self.client.describe_instances(Filters=[
            {
                'Name': 'image-id',
                'Values': [
                    IMAGE_ID,
                ]
            },
        ], )
        ids = list(map(lambda i: i['Instances'][0]['InstanceId'], response['Reservations']))
        return list(map(lambda i: self.ec2.Instance(i), ids))
