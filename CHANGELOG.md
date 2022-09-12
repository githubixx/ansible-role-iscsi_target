# Changelog

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
