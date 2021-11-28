#!/usr/bin/python

DOCUMENTATION = '''
---
module: targetcli_preferences
short_description: TargetCLI iSCSI target module for managing global preferences
description:
     - module for handling iSCSI global preferences in targetcli ('/iscsi').
     - Global preferences are not stored with targetcli configuration.
     - Stored in user's directory $HOME/.targetcli
     - 'targetcli get global' obtain global preferences
     - 'targetcli get global <pref_name>' obtain value of one of the preferences
     - 'targetcli set global <pref_name>=<value> set the preference to a specific value
     
version_added: "2.0"
options:
  preference:
    description:
      - name of the global preference
    required: true
    default: null
  value:
    description:
      - Value of the global preference
    required: true
    default: nulle
notes:
   - Tested on Archlinux, Ubuntu 20.04
requirements: [ ]
author: "Ricardo Sanchez <ricsanfre@gmail.com>"
'''

EXAMPLES = '''
define new new value for a global preference
- targetcli_preferences: preference=auto_add_mapped_luns value=false

'''

from distutils.spawn import find_executable

def main():
        module = AnsibleModule(
                argument_spec = dict(
                        preference=dict(required=True),
                        value=dict(required=True),
                ),
                supports_check_mode=True
        )

        preference = module.params['preference']
        value = module.params['value']

        if find_executable('targetcli') is None:
            module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

        result = {}

        try:
            rc, out, err = module.run_command("targetcli 'get global %(preference)s'" % module.params)
            row_data = out.split('\n')[0].split('=')
            already_set = False
            if row_data[0] == preference and row_data[1].strip() == value:
                already_set = True
            if rc == 0 and already_set:
                result['changed'] = False
            elif rc == 0 and not already_set:
                if module.check_mode:
                    module.exit_json(changed=True)
                else:
                    rc, out, err = module.run_command("targetcli 'set global %(preference)s=%(value)s'" % module.params)
                    if rc == 0:
                        module.exit_json(changed=True)
                    else:
                        module.fail_json(msg="Failed to change preference")
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI object - %s" %(e) )
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
