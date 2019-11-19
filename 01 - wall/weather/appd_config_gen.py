import os, socket
hostname = socket.gethostname()
node_id = hostname.split('-')[-1]

# Flush appdynamics.cfg before start
open('appdynamics.cfg', 'w').close()

try:
    with open("appdynamics.cfg", "a") as appdconfig:
        appdconfig.write("[agent]\napp = " + os.environ['appd_appname'] +
                         "\ntier = " + os.environ['appd_tiername'] +
                         "\nnode = node " + node_id +
                         "\n\n[controller]\nhost = " + os.environ['appd_hostname'] +
                         "\nport = " + os.environ['appd_port'] +
                         "\nssl = " + os.environ['appd_sslenabled'] +
                         "\naccount = " + os.environ['appd_account'] +
                         "\naccesskey = " + os.environ['appd_accesskey'] + "\n\n")
except Exception:
    print('Unable to create AppD config file. Not all variables have values')