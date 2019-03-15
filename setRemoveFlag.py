#!/usr/bin/python
import os
tag = "delete:yes"
cmd = "nxinfo shell -t csv -e \"select source.id where source.tags='[s]" + tag + "' or source.tags='[u]" + tag + "' and source.storage!=remove\""
output = os.popen(cmd).read()
ids = output.split("\n")[1:-1]
if len(ids)==0:
   print "nothing to do."
   exit(1)

# create a list of all update-commands:
cmdlist = []
for id in ids:
   cmd = "update source.storage=remove where source.id=" + id
   cmdlist.append(cmd) 

# write all update-commands into a file:
import tempfile
filename = tempfile.NamedTemporaryFile(delete=True).name
file = open(filename, 'w')
file.write('\n'.join(cmdlist))
file.close()

# execute all commands via nxinfo:
cmd = "nxinfo shell -f " + filename
output = os.popen(cmd).read()
exit(0)
