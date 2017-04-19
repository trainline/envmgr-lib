# Copyright (c) Trainline Limited, 2017. All rights reserved. See LICENSE.txt in the project root for license information.

from envmgr import EmClient

class Upstream(object):

    def __init__(self, service, slice, env, name=None):
        self.service = service
        self.slice = slice
        self.env = env
        self.name = name
        self.client = EmClient()

    def get_status(self):
        """
        Compare the active status of upstream hosts to configured state
        """
        upstream_name = self.get_name()
        load_balancers = self.get_load_balancers()
        status = self.__get_active_status(upstream_name, load_balancers)
        config = [ config for config in status['upstream_config'] if config['name'] == self.slice ][0]
        slice_active = config.get('active')
        slice_state = 'up' if slice_active else 'down'
        matching_upstreams = [ u for u in status['upstream_status'] if u['port'] == config['port'] ]
        toggled_upstreams = [ u for u in matching_upstreams if u['active'] is True ]
        n_total = len(matching_upstreams)
        n_ready = len(toggled_upstreams)
        n_lb = len(load_balancers)
        toggle_complete = slice_active and n_ready is n_total and n_ready is not 0
        return UpstreamStatus(toggle_complete, self.slice, slice_state, n_ready, n_total, n_lb)

    def get_name(self):
        if self.name is None:
            svc_slices = self.client.get_service_slices(self.service, self.env)
            svc_slices = [ s for s in svc_slices if s.get('Name').lower() == self.slice ]
            if len(svc_slices) > 1:
                raise Exception('Multiple upstreams are attached to {0}, provide one via the constructor'.format(self.service))
                return
            else:
                self.name = svc_slices[0].get('UpstreamName')
        return self.name

    def get_load_balancers(self):
        env_type_name = self.client.get_environment_config(self.env).get('Value').get('EnvironmentType')
        env_type = self.client.get_environmenttype_config(env_type_name)
        load_balancers = list(env_type.get('Value').get('LoadBalancers'))
        return load_balancers

    def __get_active_status(self, upstream_name, load_balancers):
        all_upstreams = reduce(lambda a,b: a + self.client.get_loadbalancer(b), load_balancers, [])
        lb_upstreams = [ upstream for upstream in all_upstreams if upstream.get('Name') == upstream_name ] 
        lb_upstreams = reduce(lambda a,b: a + b.get('Hosts'), lb_upstreams, [])
        lb_upstreams = map(host_to_upstream, lb_upstreams)
        lb_config = map(slice_to_upstream, self.client.get_upstream_slices(upstream_name, self.env))
        return {'upstream_status':lb_upstreams, 'upstream_config':lb_config}


class UpstreamStatus(object):
    def __init__(self, is_active, slice, slice_config, active_upstreams, total_upstreams, total_load_balancers):
        self.is_active = is_active
        self.slice = slice
        self.slice_config = slice_config
        self.active_upstreams = active_upstreams
        self.total_upstreams = total_upstreams
        self.total_load_balancers = total_load_balancers


def host_to_upstream(host): 
    return {
        'active': get_active_state(host.get('State')),
        'port': int(host.get('Server').split(':')[1])
    }

def slice_to_upstream(slice):
    return {
        'port': slice.get('Port'),
        'name': slice.get('Name').lower(),
        'active': get_active_state(slice.get('State'))
    }

def get_active_state(state):
    state = state.lower()
    return True if state == 'up' or state == 'active' else False
