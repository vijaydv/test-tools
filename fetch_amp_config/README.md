Get the AMP config parameters from all the appliances present in a HTML page

$ python fetch_amp_config.py --help
Usage: fetch_amp_config.py [options]

Options:
  -h, --help            show this help message and exit
  -m MACHINE_LIST, --machinelist=MACHINE_LIST
                        provide comma separated machine list
  -u LAB_URL, --url=LAB_URL
                        netinstall lab url page. Provide either lab url link
                        or machine list, not both. If both machine list and
                        URL are not provided, then all machines in IBQA
                        netinstall page(http://install.ibqa/netinstall.cgi) is
                        used
