#!/usr/bin/python
import csv, json, os 
import logging 

log = logging.getLogger(__name__)
CUR_DIR = os.path.dirname(os.path.abspath(__file__))

# check to ensure requests + yaml are available 
try: 
	import requests
	REQUESTS_LOADED = True 
except ImportError:
	REQUESTS_LOADED = False 
	log.exception('requests package is required') 
try:
	import yaml
	YAML_LOADED = True 
except ImportError:
	YAML_LOADED = False 
	log.exception('yaml package is required') 


def __virtual__():
	if REQUESTS_LOADED == True and YAML_LOADED == True:
		return True 
	return False

def get_config(cfgpath):
    if not os.path.exists(cfgpath):
        if not os.path.exists(os.path.join(CUR_DIR, cfgpath)):
            raise ValueError("Config file %s is not found!" % cfgpath)
    cfgpath = os.path.join(CUR_DIR, cfgpath)
    with open(cfgpath, 'r') as cfgf:
        config = yaml.load(cfgf.read())
	return config

def _req(url, payload, auth, headers, verify=True):

    response = requests.request(
        "POST",
        url,
        data=payload,
        auth=auth,
        headers=headers,
        verify=verify
    )
    return response

def request_minion_info(query, config):

    payload = {
        "query": query,
        "header": "yes"
    }
    
    headers={'Accept': 'application/json'}
    auth = (config['user'], config['pass'] )
    url = "%s/services/data/v1.0/query/" % config['host']
    verify = False

    response = _req(url, payload, auth, headers, verify)

    return response

def generate_simple_query(fields, nodename):
	selectors = ""
	if len(fields) > 1:
		for f in fields:
			if isinstance(f, basestring):
				print 'yes: ' + f
				selectors += "%s," % f
			else:
				# throw exception for type error 
				print 'no: ' + f
		selectors = selectors[:-1] # remove coma which will trail this due to loop above    
	else: # only 1 field in fields...
		selectors += fields
	# write the simple query 
	query = " SELECT %s FROM view_device_v1 WHERE name = '%s' " % (selectors, nodename) # put selectors and nodename into simple query
	return query

def generate_fields_to_get(conf):
    query = ""
    if len(conf) > 1:
        for c in conf:
            if isinstance(c, basestring):
                print 'yes: ' + c
                query += "%s," % c
            else:
                print 'no: ' + c
    else:
        query += conf
    return query[:-1]

def ext_pillar(minion_id, pillar, arg0):
	log.info("running d42 ext_pillar") 
 
	nodename = __grains__['nodename']
	config = get_config('settings_d42.yaml') 
	if config['query'] != None:
		query = config['query'].format(minion_name=nodename)
	else:
		query = generate_simple_query(config['default_fields_to_get'], nodename)
	
	response = request_minion_info(query, config)	
	listrows = response.text.split('\n')
	fields = listrows[0].split(',')
	rows = csv.reader(listrows[1:])
	out = []
	for row in rows:
		items = zip(fields, row)
		item = {}
		for (name, value) in items:
			item[name] = value.strip()
		out.append(item)
	
	data = {
		'minion_id': minion_id,
		'd42': out[0]
	}
	log.warning("out->  " + json.dumps(data, indent=4, sort_keys=True))  
	return data
