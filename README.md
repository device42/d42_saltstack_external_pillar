# d42 salt external pillar


## What:
A simple external pillar module for Salt that allows for importing Device42 fields into Salt Pillars.  

## Why:
By syncing data stored in your Device42 CMDB with their respective servers / minions as managed by Salt, all of your configuraiton information feeds into granular, actionable salt commands.  This information can be used to power any number of automations: 
- provisioning a new server based on classifications in Device42.
- remediating an issue with a proven workflow.
- performing maitnence on all servers in a specific environment (Production, Staging, Development, etc)
- gathering specific information about a server for use in ITSM ticketing software.  

## How: 
The D42 Salt External Pillar will query D42 for a set of fields with respect to each of your salt minions configured to utilize it.  The set of fields from D42 can be configured based on raw DOQL queries or can be generically used to fetch fields from the main device table in D42.  

## Installation

Edit `/etc/salt/master` on your Salt Master so that it knows to look for the d42 external pillars module
```
extension_modules: /srv/ext # a common location for salt modules 
ext_pillar:
  - d42:
```

Clone this repo.  Fill in your information into the settings example and rename it to `settings_d42.yaml`

Move `d42.py` and `settings_d42.yaml` into `/srv/ext/pillar` 

Restart your salt master and salt minion services 
```
$ service salt-master restart 
$ service salt-minion restart
```

Refresh your Salt Pillars across all your minion devices: 
```
$ salt '*' saltutil.refresh_pillar 
```

Test that you're d42 pillar has data in it:
```
$ salt '*' pillar.items
ubuntu:
    ----------
    d42:
        ----------
        os_name:
            Ubuntu
        os_version:
            14.04
        salt_node_id:
            ubuntu.saltmaster5
        service_level:
            Production
        tags:
            saltmaster,salt
    minion_id:
        ubuntu
    nodename:
        ubuntu.saltmaster5
```

Check out [D42 Blog](device42.com/blog) for a post on this new integration shortly! 

Please get in touch with any questions or help with designing your integration 

 

