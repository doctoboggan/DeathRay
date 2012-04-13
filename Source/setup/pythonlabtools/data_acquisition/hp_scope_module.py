"module importing a scope for global access"
_rcsid="$Id: hp_scope_module.py 323 2011-04-06 19:10:03Z marcus $"

from vxi_11_scopes import hp54542

class my_hp54542(hp54542):
	pass
	
		
if 0:
	scope=my_hp54542(host="129.59.235.196", portmap_proxy_host="127.0.0.1", portmap_proxy_port=1111,
			 device="gpib0,7",  timeout=4000, device_name="hp54542",
			raise_on_err=1)
else:
	scope=my_hp54542(host="129.59.235.196", 
			 device="gpib0,7",  timeout=5000, device_name="hp54542",
			raise_on_err=1)

