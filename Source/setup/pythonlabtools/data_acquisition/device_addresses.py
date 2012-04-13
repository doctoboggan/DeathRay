"Lots of miscellaneous device configuration information to be imported globally in a typical installation"
_rcsid="$Id: device_addresses.py 323 2011-04-06 19:10:03Z marcus $"

if 0:
	proxy="127.0.0.1"
	proxy_port=1111
else:
	proxy=None
	proxy_port=111

crate_host="129.59.235.230"
crate_portmap_proxy_host=proxy
crate_portmap_proxy_port=proxy_port
crate_using_e5810=1

magnet_host="129.59.235.230"
magnet_portmap_proxy_host=proxy
magnet_portmap_proxy_port=proxy_port
magnets_using_e5810=1

e1413b_scan_list=("(@5(00:8),7(9,9,9),5(9:13),7(14,14,14),5(14:18),7(19,19,19),"
	"5(19,46,47,43,45,44,40),7(20,20,20,20),5(20:35),5(50,51),5(36),"
	"7(37,37,37),5(37:39,41:42))")
e1413b_scan_channels=50

