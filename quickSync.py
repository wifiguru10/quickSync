#!ipython3 -i 

import meraki


#########
API = "" #put your API key in here


######

if API == "":
	import get_keys as g
	API = g.get_api_key()

def findName(list_of_things, target_name):
    res = []
    for o in list_of_things:
        if target_name in o['name']:
            res.append(o)
        if target_name == o['name']:
            return [o] #done here, short circuit, need exact match
    return res

db = meraki.DashboardAPI(api_key=API, base_url='https://api.meraki.com/api/v1/', maximum_retries=50, print_console=False)

orgs = db.organizations.getOrganizations()

res = []
print()

while len(res) != 1:
	print('Enter Organization Name:')
	res = findName(orgs, input())
	if len(res) > 1:
		for r in res:
			print(f"found Org[{r['name']}]")
	print()

if len(res) == 1:
	print(res[0])
	org_id = res[0]['id']

devs = db.organizations.getOrganizationDevices(org_id)

nets = db.organizations.getOrganizationNetworks(org_id)

res = []
source_netid = None
while len(res) != 1:
    print('Enter SOURCE Name:')
    res = findName(nets, input())
    
    if len(res) > 1:
        for r in res:
            print(f"found Network[{r['name']}]")
    print()

if len(res) == 1:
	source_netid = res[0]['id']

syslog = db.networks.getNetworkSyslogServers(source_netid)
netflow = db.networks.getNetworkNetflow(source_netid)

print()
print ("This is now going to go through all networks in this org and configure the settings")
print()

for n in nets:
    if n['id'] == source_netid: continue #don't update the golden
    ans = 'n' #Set this to 'y' to bypass and always write
    print(f"Do you want to write the settings to Network[{n['name']}]?")
    if ans == 'n': ans = input("(y/N): ")
    if not ans == 'y': continue
    try:
        db.networks.updateNetworkSyslogServers(n['id'], **syslog)
        print(f"\tSyslog Written to Network[{n['name']}]")
        db.networks.updateNetworkNetflow(n['id'],**netflow)
        print(f"\tNetflow Written to Network[{n['name']}]")
        print()

    except Exception as e:
        print(f"\t\t EXCEPTION applying config to network[{n['name']}]")
        print(e)
        print()

print()


