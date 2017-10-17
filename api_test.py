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


def request_minion_info(fields_to_get, nodename):
	payload = {
		"query": "SELECT %s FROM view_device_v1 WHERE name = '%s' order by device_pk" % (fields_to_get, nodename), 
		"header": "yes"
	}
	print 'generated payload: ' + json.dumps(payload, indent=4) 
	headers={'Accept': 'application/json'} 
	auth = ('admin', 'adm!nd42')
	config = get_config('settings.yaml')
	url = "https://10.42.2.241/services/data/v1.0/query/"
	verify = False 
	print "config: %s" % config 
	response = _req(url, payload, auth, headers, verify) 
	return response 
 
def main(): 
	mapping = "*"  # get all, placeholder for now, but pretty cool tbh 
	nodename = 'ubuntu.saltmaster5'
	
	response = request_minion_info(mapping, nodename) 
	
	print(response.text)
	listrows = response.text.split('\n')

	print listrows

	fields = listrows[0].split(',')
	rows = csv.reader(listrows[1:])
	out = []

	for row in rows:
		items = zip(fields, row)
		item = {}
		for (name, value) in items:
			item[name] = value.strip()
		out.append(item)
	print "output: " + json.dumps(out, indent=4, sort_keys=True) 

	return out 
	'''
	print "\n-------------------- "
	print("Response: "  + str(response.text))
	print "\n-------------------- "
	listrows = response.text.split('\n') 

	# print listrows

	fields = listrows[0].split(',') 
	rows = csv.reader(listrows[1:])
	out = []

	for row in rows:
		items = zip(fields, row)
		item = {}
		for (name, value) in items:
			item[name] = value.strip()
    	out.append(item)

	print json.dumps(out, indent=4, sort_keys=True)
	# print 'service level: ' + json.dumps(out[0]['service_level'], indent=4, sort_keys=True)
	
	return out
	'''

obj = main()

# --------------------
url = "https://10.42.2.241/services/data/v1.0/query/"

print json.dumps(obj, indent=4, sort_keys=True)

payload = {
    'query': "SELECT * FROM view_device_v1 WHERE name = 'ubuntu.saltmaster5' order by device_pk",
    'header': 'yes'
}

response = requests.request(
    "POST",
    url,
    data=payload,
    auth=('admin', 'adm!nd42'),
    headers={'Accept': 'application/json'},
    verify=False
)

print(response.text)
listrows = response.text.split('\n') 

print listrows

fields = listrows[0].split(',') 
rows = csv.reader(listrows[1:])
out = []

for row in rows:
	items = zip(fields, row)
	item = {}
	for (name, value) in items:
		item[name] = value.strip() 
	out.append(item)

print json.dumps(out, indent=4, sort_keys=True)	
print 'service level: ' + json.dumps(out[0]['service_level'], indent=4, sort_keys=True)	
