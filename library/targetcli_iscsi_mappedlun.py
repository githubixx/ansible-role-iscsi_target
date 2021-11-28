#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi_mappedlun
short_description: TargetCLI iSCSI mapped luns module
description:
     - module for setting iSCSI mapped luns  parameters in targetcli ('/iscsi/.../tpg1').
version_added: "2.4"
options:
  wwn:
    description:
      - WWN of iSCSI target (server)
    required: true
    default: null
  initiator_wwn:
    description:
      - WWN of iSCSI initiator (client)
    required: true
    default: null
  mapped_lunid:
    description:
      - mapped lun id
    required: true
    default: null
  lunid:
    description:
      - associated lun id
    required: true
    default: null
  write_protec:
    description:
      - whether the initiator will have write access to the Mapped LUN
    required: false
    default: 0
    choices: [0, 1]
  state:
    description:
      - Should the object be present or absent from TargetCLI configuration
    required: false
    default: present
    choices: [present, absent]

notes:
   - Tested on Archlinux, Ubuntu 20.04
requirements: [ ]
author: "Ricardo Sanchez <ricsanfre@gmail.com>"
'''

EXAMPLES = '''
Define new mapped LUN
- targetcli_iscsi_mappedlun: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest initiator_wwn=iqn.1994-05.com.redhat:client1 mapped_lunid=0 lunid=0

Define new mapped LUN with write protect

- targetcli_iscsi_mappedlun: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest initiator_wwn=iqn.1994-05.com.redhat:client1 mapped_lunid=0 lunid=0 write_protect=1

Remove mapped LUN

- targetcli_iscsi_mappedlun: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest initiator_wwn=iqn.1994-05.com.redhat:client1 mapped_lunid=0 lunid=0 state=absent

'''

from distutils.spawn import find_executable
import re

def main():
  module = AnsibleModule(
    argument_spec=dict(
      wwn=dict(required=True),
      initiator_wwn=dict(required=True),
      lunid=dict(required=True),
      mapped_lunid=dict(required=True),
      write_protect=dict(default="0", choices=['0', '1']),
      state=dict(default="present", choices=['present', 'absent']),
    ),
    supports_check_mode=True)

  if find_executable('targetcli') is None:
    module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")
  state = module.params['state']
  initiator_wwn = module.params['initiator_wwn']
  mapped_lunid = module.params['mapped_lunid']
  mapped_luns = {}
  result = {}
  try:
    rc, out, err = module.run_command("targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s status'" % module.params)
    if rc != 0:
      module.fail_json(msg="Referenced initiator acl does not exist.")
    
    # get list of mapped luns
    rc, out, err = module.run_command(
      "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s ls'" % module.params)
    
    for row in out.split('\n'):
        row_data = row.split(' ')
        if len(row_data) < 2 or row_data[0] == initiator_wwn:
            continue
        if row_data[1] == initiator_wwn:
            continue
        mapped_luns[row_data[3][10:]] = row_data[5][4:]
        # mapped_luns['mapped_lun_id']= lun_id
    
    if state == 'present' and mapped_lunid in mapped_luns:
        # Mapped LUN is already there and present
        result['changed'] = False
        result['lun_id'] = mapped_luns[mapped_lunid]
    elif state == 'absent' and not mapped_lunid in mapped_luns:
        # Mapped LUN is not there and should not be there
        result['changed'] = False
    elif state == 'present' and not mapped_lunid in mapped_luns:
        # create mapped LUN
        rc, out, err = module.run_command(
          "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s create mapped_lun=%(mapped_lunid)s tpg_lun_or_backstore=%(lunid)s write_protect=%(write_protect)s'"
          % module.params)
        if rc == 0:
          module.exit_json(changed=True)
        else:
          module.fail_json(msg="Failed to set iSCSI mapped luns")
    elif state == 'absent' and mapped_lunid in mapped_luns:
        # delete mapped LUN
        if module.check_mode:
            module.exit_json(changed=True)
        else:
            rc, out, err = module.run_command(
              "targetcli '/iscsi/%(wwn)s/tpg1/acls/%(initiator_wwn)s delete mapped_lun=%(mapped_lunid)s'"
               % module.params )
            if rc == 0:
                module.exit_json(changed=True)
            else:
                module.fail_json(msg="Failed to delete iSCSI mapped LUN object")
  except OSError as e:
    module.fail_json(msg="Failed to check iSCSI mapped luns - %s" % (e))
  module.exit_json()


# import module snippets
from ansible.module_utils.basic import *
main()
