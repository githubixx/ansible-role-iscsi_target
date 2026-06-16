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
    - Tested on Archlinux, Ubuntu 22.04, Ubuntu 24.04, Ubuntu 26.04
requirements: [ ]
author: "Ricardo Sanchez <ricsanfre@gmail.com>"
'''

EXAMPLES = '''
define new new value for a global preference
- targetcli_preferences: preference=auto_add_mapped_luns value=false

'''

from shutil import which
import os
import pickle


def read_preference(module, preference):
    rc, out, err = module.run_command(
        "targetcli 'get global %(preference)s'" % module.params
    )
    if rc != 0:
        module.fail_json(
            msg="Failed to read preference",
            preference=preference,
            rc=rc,
            stdout=out,
            stderr=err,
        )

    row_data = out.split('\n')[0].split('=', 1)
    if len(row_data) != 2 or row_data[0] != preference:
        module.fail_json(
            msg="Failed to parse preference output",
            preference=preference,
            stdout=out,
            stderr=err,
        )

    return row_data[1].strip(), out, err


def normalize_preference_value(value, current_value=None):
    lowered = str(value).lower()

    if isinstance(current_value, bool):
        return lowered == 'true'

    if isinstance(current_value, int):
        try:
            return int(value)
        except ValueError:
            return value

    if lowered in ('true', 'false'):
        return lowered == 'true'

    return value


def update_preference_file(preference, value):
    prefs_dir = os.path.join(os.path.expanduser('~'), '.targetcli')
    prefs_path = os.path.join(prefs_dir, 'prefs.bin')

    if os.path.exists(prefs_path):
        with open(prefs_path, 'rb') as file_handle:
            preferences = pickle.load(file_handle)
    else:
        preferences = {}

    current_value = preferences.get(preference)
    preferences[preference] = normalize_preference_value(value, current_value)

    if not os.path.isdir(prefs_dir):
        os.makedirs(prefs_dir)

    with open(prefs_path, 'wb') as file_handle:
        pickle.dump(preferences, file_handle)

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

        if which('targetcli') is None:
            module.fail_json(msg="'targetcli' executable not found. Install 'targetcli'.")

        result = {}

        try:
            current_value, out, err = read_preference(module, preference)

            if current_value == value:
                result['changed'] = False
                module.exit_json(**result)

            if module.check_mode:
                module.exit_json(changed=True)

            rc, set_out, set_err = module.run_command(
                "targetcli 'set global %(preference)s=%(value)s'" % module.params
            )
            if rc != 0:
                module.fail_json(
                    msg="Failed to change preference",
                    preference=preference,
                    value=value,
                    rc=rc,
                    stdout=set_out,
                    stderr=set_err,
                )

            updated_value, verify_out, verify_err = read_preference(module, preference)
            if updated_value == value:
                module.exit_json(changed=True)

            update_preference_file(preference, value)
            updated_value, verify_out, verify_err = read_preference(module, preference)
            if updated_value == value:
                module.exit_json(changed=True, fallback='prefs.bin')

            module.fail_json(
                msg="Failed to verify preference change",
                preference=preference,
                value=value,
                stdout=set_out,
                stderr=set_err,
                verify_stdout=verify_out,
                verify_stderr=verify_err,
            )
        except OSError as e:
            module.fail_json(msg="Failed to check iSCSI object - %s" %(e) )
        module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
