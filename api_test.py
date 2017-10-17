import requests, csv, json, yaml, os

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


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


def request_minion_info(fields_to_get, nodename, config):
	payload = {
		"query": "SELECT %s FROM view_device_v1 WHERE name = '%s' order by device_pk" % (fields_to_get, nodename), 
		"header": "yes"
	}
	print 'generated payload: ' + json.dumps(payload, indent=4) 
	headers={'Accept': 'application/json'} 
	auth = (config['user'], config['pass'] )
	url = "%s/services/data/v1.0/query/" % config['host']
	verify = False 
	
	response = _req(url, payload, auth, headers, verify) 
	
	return response 
 

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

def main(): 
	
	config = get_config('settings.yaml')
	
	query = generate_fields_to_get(config['fields_to_get']) 
	nodename = 'ubuntu.saltmaster5'
	
	response = request_minion_info(query, nodename, config) 
	
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
	print "output: " + json.dumps(out[0], indent=4, sort_keys=True) 
	return out 

obj = main()
