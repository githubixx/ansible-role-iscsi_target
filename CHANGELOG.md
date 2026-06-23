# Changelog

## 3.0.0

- remove support for Ubuntu 20.04 (EOL)
- add Ubuntu 24.04 support
- add Ubuntu 26.04 support
- fix custom Ansible modules for Python 3.12 by replacing `distutils.spawn.find_executable`
- Ubuntu: stop installing `python3-distutils`, which is no longer available on Ubuntu 24.04+
- Molecule: remove Ubuntu 20.04 test and add Ubuntu 24.04 and Ubuntu 26.04 tests
- Molecule: remove leftover libvirt volumes during `molecule destroy`
- add dual-stack Molecule coverage and document IPv6 portal support
- handle targetcli default IPv6 portal `::0` as a special create case
- Molecule: strengthen `verify` coverage for targets, backstores, LUNs, ACLs, auth, mapped LUNs, preferences, and portals
- targetcli preferences: verify preference changes and fall back to updating `prefs.bin` when Ubuntu 26.04 `targetcli` reports success without changing state

## 2.0.0

- remove support of Ubuntu 18.04 (EOL)
- `handlers/main.yml`: supplying `yes` to `targetcli` command is no longer needed
- Archlinux: allow `iscsi_archlinux_aur_helper` to be set to empty string
- add `.yamllint`
- add `.ansible-lint`
- Github Actions: fix Ansible Galaxy import
- fix various `ansible-lint` issues
- Molecule: fix `prepare.yml` for Archlinux
- Molecule: increase instances memory

## 1.2.0

- add Ubuntu 22.04 support
- add Molecule test for Ubuntu 22.04
- add Molecule `verify` stage
- various changes im Molecule test
- `min_ansible_version` variable value should be string / versions should be string in `meta/main.yml`
- add Github release action to push new release to Ansible Galaxy
- fix various `ansible-lint` issues

## 1.1.0

- add Molecule test for Ubuntu 18.04

## 1.0.0

- initial commit

Main differences to the original version:

- added Archlinux support
- Molecule test for Archlinux
- separate task for Ubuntu and Archlinux to make it easier to support other OSes in the future
