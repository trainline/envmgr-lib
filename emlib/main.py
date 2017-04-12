
import emlib

from emlib import ASG, Service

emlib.config('environmentmanager.corp.local', 'user', 'pass')

asg = ASG('c50-in-C50EnvironmentManager', 'c50')
print(asg.exists())
print(asg.get_status())
print(asg.get_schedule())
print(asg.get_health())
print(asg.set_schedule('on'))

service = Service('TabletWeb', 'st1')
print(service.get_health())
print(service.get_health('green'))
print(service.get_slice())
print(service.get_slice(False))
