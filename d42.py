#!/usr/bin/python
import requests, csv, json

'''
WIP
'''

def api_interaction(nodename):

	url = "https://10.42.2.241/services/data/v1.0/query/"

	payload = {
	'query': "SELECT * FROM view_device_v1 WHERE name = '%s'order by device_pk" % nodename,
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

	# print(response.text)
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
	# print json.dumps(out, indent=4, sort_keys=True)                                                     
	return out

def ext_pillar(minion_id, pillar, arg0):
	nodename = __grains__['nodename']	
	
	d42_data = api_interaction(nodename) 

		
	
	data = {
		'minion_id': minion_id, 
		'test': 'out', 
		'masterconf_arg0': arg0,
		'nodename': nodename,
		'd42': d42_data[0]
	}
	return data
