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
'''
this is what is returned from the view_device_custom_fields_v1 table 
{
    "device_fk": "19", 
    "device_name": "ubuntu.saltmaster5", 
    "filterable": "f", 
    "is_multi": "f", 
    "key": "Salt Node ID", 
    "log_for_api": "t", 
    "mandatory": "f", 
    "related_model_name": "", 
    "type": "Text", 
    "type_id": "1", 
    "value": "ubuntu.saltmaster5"
}

'''

def request_minion_info(query, config):
	
	payload = {
		"query": query,
		#"query": "SELECT %s FROM view_device_v1, view_device_custom_fields_v1 WHERE view_device_v1.name = '%s' AND view_device_v1.name=view_device_custom_fields_v1.device_name" % (fields_to_get, nodename), 
		# original "query": "SELECT %s FROM view_device_v1 WHERE name = '%s'" % (fields_to_get, nodename),
		# works "query": "SELECT %s FROM view_device_custom_fields_v1 WHERE device_name='%s' " % (fields_to_get, nodename),
		"header": "yes"
	}
	print 'generated payload: ' + json.dumps(payload, indent=4) 
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


def generate_custom_fields_subquery(custom_fields): 
	subqueries = ""
	for c in custom_fields:
		print 'key: ' + str(c.keys() ) 
		print 'values: ' + str(c.values() )
		custom_fieldname=c.keys()[0] 
		alias = c.values()[0]
		query = '(SELECT value FROM view_device_custom_fields_v1 WHERE device_fk = device_pk AND key = "{fieldname}" ) AS "{fieldname_alias}",'.format(fieldname=custom_fieldname, fieldname_alias=alias)
		# print query 
		subqueries += query
	
	return subqueries[:-1] # parse out final coma

def main(): 
	
	config = get_config('settings.yaml')
	# query = '*'
	nodename = 'ubuntu.saltmaster5'
	# query = generate_simple_query(config['fields_to_get']) 
	
	subqueries = generate_custom_fields_subquery(config['custom_fields_to_get']) 	
	print 'subqueries: ' + subqueries 
	if config['query'] != None:	
		query = config['query'].format(nodename=nodename, subqueries=subqueries)
	else: 
		query = generate_simple_query(config['fields_to_get'], nodename) 

	print '\n\n query: %s \n\n ' % (query)
	
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
	print "output: " + json.dumps(out[0], indent=4, sort_keys=True) 
	return out 

obj = main()
