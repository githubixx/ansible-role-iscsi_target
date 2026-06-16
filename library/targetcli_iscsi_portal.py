#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_iscsi_portal
short_description: TargetCLI iSCSI portal module
description:
     - module for handling iSCSI portal objects in targetcli ('/iscsi/.../tpg1/portals').
version_added: "2.4"
options:
  wwn:
    description:
      - WWN of iSCSI target (server)
    required: true
    default: null
  ip:
    description:
      - IP where the target shall be exported on
    required: true
    default: null
  port:
    description:
      - port where the target shall be exported on
    required: false
    default: 3260
  state:
    description:
      - Should the object be present or absent from TargetCLI configuration
    required: false
    default: present
    choices: [present, absent]
notes:
  - Tested on Archlinux, Ubuntu 22.04, Ubuntu 24.04, Ubuntu 26.04
requirements: [ ]
author: "Michel Weitbrecht <michel.weitbrecht@stuvus.uni-stuttgart.de>"
'''

EXAMPLES = '''
define new portal with default port
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest ip=192.168.178.55

define new portal with non-default port
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest ip=192.168.178.55 port=2881

remove the portal
- targetcli_iscsi_portal: wwn=iqn.2003-01.org.linux-iscsi.storage01.x8664:portaltest ip=192.168.178.55 port=2881 state=absent
'''

from shutil import which


def canonicalize_ip(ip_address):
    if "." in ip_address:
        return ip_address

    if ip_address.startswith("[") and ip_address.endswith("]"):
        return ip_address

    return "[{}]".format(ip_address)


def is_default_ipv6_portal(ip_address, port):
    return ip_address == "::0" and str(port) == "3260"


def main():
  module = AnsibleModule(
    argument_spec=dict(
      wwn=dict(required=True),
      ip=dict(required=True),
      port=dict(default="3260"),
      state=dict(default="present", choices=['present', 'absent']),
    ),
    supports_check_mode=True
  )

  state = module.params['state']
  portal_path_params = dict(module.params)
  portal_path_params['ip'] = canonicalize_ip(module.params['ip'])
  portal_cmd_params = dict(module.params)
  create_command = "targetcli '/iscsi/%(wwn)s/tpg1/portals create %(ip)s %(port)s'" % portal_cmd_params

  if is_default_ipv6_portal(module.params['ip'], module.params['port']):
    create_command = "targetcli '/iscsi/%(wwn)s/tpg1/portals create'" % portal_cmd_params

  if which('targetcli') is None:
    module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

  result = {}

  try:
    rc, out, err = module.run_command(
      "targetcli '/iscsi/%(wwn)s/tpg1/portals/%(ip)s:%(port)s status'" % portal_path_params)
    if rc == 0 and state == 'present':
      result['changed'] = False
    elif rc == 0 and state == 'absent':
      if module.check_mode:
        module.exit_json(changed=True)
      else:
        rc, out, err = module.run_command(
          "targetcli '/iscsi/%(wwn)s/tpg1/portals delete %(ip)s %(port)s'" % portal_cmd_params)
        verify_rc, verify_out, verify_err = module.run_command(
          "targetcli '/iscsi/%(wwn)s/tpg1/portals/%(ip)s:%(port)s status'" % portal_path_params)
        if verify_rc != 0:
          module.exit_json(changed=True)
        else:
          module.fail_json(
            msg="Failed to delete iSCSI portal object",
            rc=rc,
            stdout=out,
            stderr=err,
            verify_rc=verify_rc,
            verify_stdout=verify_out,
            verify_stderr=verify_err,
          )
    elif state == 'absent':
      result['changed'] = False
    else:
      if module.check_mode:
        module.exit_json(changed=True)
      else:
        rc, out, err = module.run_command(
          create_command)
        verify_rc, verify_out, verify_err = module.run_command(
          "targetcli '/iscsi/%(wwn)s/tpg1/portals/%(ip)s:%(port)s status'" % portal_path_params)
        if verify_rc == 0:
          module.exit_json(changed=True)
        else:
          module.fail_json(
            msg="Failed to define iSCSI portal object",
            rc=rc,
            stdout=out,
            stderr=err,
            verify_rc=verify_rc,
            verify_stdout=verify_out,
            verify_stderr=verify_err,
          )
  except OSError as e:
    module.fail_json(msg="Failed to check iSCSI portal object - %s" % (e))

  module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
