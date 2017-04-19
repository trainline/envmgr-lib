# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from envmgr import EmClient

class ASG(object):

    def __init__(self, name, env):
        self.name = name
        self.env = env
        self.client = EmClient()
    
    def exists(self):
        """
        Checks if the ASG exists (has been created in AWS)
        """
        try:
            asg = self.client.get_asg(self.env, self.name, retries=1)
            return True
        except:
            return False

    def get_schedule(self):
        """
        Returns the "Full ASG schedule" or None if not set
        """
        asg = self.client.get_asg(self.env, self.name)
        tags = asg.get('Tags')
        if tags is not None:
            schedule_tag = [ tag for tag in tags if tag.get('Key') == 'Schedule' ]
            if (len(schedule_tag) > 0):
                return schedule_tag[0]
        return None

    def set_schedule(self, schedule):
        """
        Sets the "Full ASG schedule" value
        """
        data = {'propagateToInstances':True, 'schedule':schedule}
        return self.client.put_asg_scaling_schedule(environment=self.env, asgname=self.name, data=data)

    def get_status(self):
        """
        Returns the "ready" status
        """
        return self.client.get_asg_ready(self.env, self.name)

    def get_health(self):
        """
        Checks the expected number of instances are running and that
        each instance is running the expected services.
        """
        asg = self.client.get_environment_asg_servers(self.env, self.name)
        service_counts = asg.get('ServicesCount')
        n_expected = service_counts.get('Expected')
        n_unexpected = service_counts.get('Unexpected', 0)
        n_missing = service_counts.get('Missing', 0)
        result = {'required_count':n_expected}

        if n_missing != 0:
            result['is_healthy'] = False
            result['missing_count'] = n_missing
            return result
        if n_unexpected != 0:
            result['is_healthy'] = False
            result['unexpected_count'] = n_unexpected
            return result
        if n_expected == 0:
            result['is_healthy'] = False
            return result

        instances = list(asg.get('Instances'))
        if not instances:
            result['is_healthy'] = False
            result['instances_count'] = 0
            return result
        
        healthy_instances = [ instance for instance in instances if instance.get('RunningServicesCount') == n_expected ]
        n_instances = len(instances)
        n_healthy = len(healthy_instances)
        result['instances_count'] = n_instances
        
        if n_healthy != n_instances:
            result['is_healthy'] = False
            result['unhealthy_count'] = (n_instances - n_healthy)
            return result
        else:
            result['is_healthy'] = True
            return result

