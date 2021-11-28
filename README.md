ansible-role-iscsi_target
=========================

This role configures a Linux-LIO based iSCSI target on a Linux host using `targetcli`. Additionally this role includes Python modules to interact with `targetcli` command which can be used separately for more advanced stuff. Modules implement checking, creating and deleting.

Tested with:

- Ubuntu 20.04
- Archlinux

Documentation about LIO and Target can be found [here](https://linux-iscsi.org/wiki/Main_Page).

Requirements
------------

This role is not creating any disks/partitions/LVs. It is expected that they are already present on machine or created by some other role. For example: [githubixx.lvm](https://github.com/githubixx/ansible-role-lvm).

Changelog
---------

see [CHANGELOG](https://github.com/githubixx/ansible-role-iscsi_target/blob/master/CHANGELOG.md)

Role Variables
--------------

```yaml
# The iSCSI target(s) is/are configured via "iscsi_targets" nested variable.
# A quite minimal setup looks like this example:
#
# iscsi_targets:
#   - name: "iqn.2021-11.blog.tauceti:{{ ansible_facts['nodename'] }}"
#     disks:
#       - name: lun_node1
#         path: /dev/vdb
#         type: block
#         lunid: 0
#     initiators:
#       - name: iqn.2021-07.blog.tauceti:node1
#         authentication:
#           userid: node1user
#           password: node1pw
#           userid_mutual: node1sharedkey
#           password_mutual: node1sharedsecret
#         mapped_luns:
#           - mapped_lunid: 0
#             lunid: 0
#     portals:
#       - ip: "0.0.0.0"
#
# For more information see README.
iscsi_targets: []
```

The configuration above will create an iSCSI setup that will look like this (Output generated with `targetcli 'ls'`):

```plain
# o- / .................................................................................... [...]
#   o- backstores ......................................................................... [...]
#   | o- block ............................................................. [Storage Objects: 1]
#   | | o- lun_node1 ................................... [/dev/vdb (1.0GiB) write-thru activated]
#   | |   o- alua .............................................................. [ALUA Groups: 1]
#   | |     o- default_tg_pt_gp .................................. [ALUA state: Active/optimized]
#   | o- fileio ............................................................ [Storage Objects: 0]
#   | o- pscsi ............................................................. [Storage Objects: 0]
#   | o- ramdisk ........................................................... [Storage Objects: 0]
#   o- iscsi ....................................................................... [Targets: 1]
#   | o- iqn.2021-11.blog.tauceti:ubuntu .............................................. [TPGs: 1]
#   |   o- tpg1 .......................................................... [no-gen-acls, no-auth]
#   |     o- acls ..................................................................... [ACLs: 1]
#   |     | o- iqn.2021-07.blog.tauceti:node1 .................................. [Mapped LUNs: 1]
#   |     |   o- mapped_lun0 ........................................ [lun0 block/lun_node1 (rw)]
#   |     o- luns ..................................................................... [LUNs: 1]
#   |     | o- lun0 ............................. [block/lun_node1 (/dev/vdb) (default_tg_pt_gp)]
#   |     o- portals ............................................................... [Portals: 1]
#   |       o- 0.0.0.0:3260 ................................................................ [OK]
#   o- loopback .................................................................... [Targets: 0]
#   o- vhost ....................................................................... [Targets: 0]
#   o- xen-pvscsi .................................................................. [Targets: 0]
```

`iscsi_targets.name` specifies the name of the iSCSI target (the iSCSI server so to say). As you can see above this entry will appear under the `iscsi` node in the `targetcli` output.

`disks` create one or more block storage object(s). In this case it will be called `lun_node1`, the LUN ID will be `0`. The storage type will be a `block` device which in this case is located at `/dev/vdb`. This device can (and maybe even should) be a logical volume too of course.

`initiators` defines all iSCSI initiators (the iSCSI clients - if you want - which wants to access the iSCSI target specified above). Every iSCSI initiator host (client) that wants to connect the iSCSI target (server) needs an entry here. The iSCSI initiator name normally can be found in `/etc/iscsi/initiatorname.iscsi` on every initiator (client) after `open-iscsi` package has been installed. The `authentication` object contains either only `userid` and `password` and optional also `userid_mutual` plus `password_mutual`.

`mapped_luns` assigns mapped LUNs (logical units) to initiator. Normally `mapped_lunid` and `lunid` matches the same `lunid` in `iscsi_targets.disks`. But it also could be different.

`portals` allows to specify the IP address the iSCSI target service should listen on. E.g. if `0.0.0.0` is specified then the service will listen on all interfaces on port `3260`. Of course Ansible facts can also be used e.g. `{{ ansible_default_ipv4.address | default(ansible_all_ipv4_addresses[0]) }}`.

```yaml
#######################################
# Settings only relevant for Archlinux
#######################################

# "targetcli-fb" package is needed to configure iSCSI target. For Archlinux
# this package needs to be installed from AUR. This requires an AUR install
# helper like "yay", "paru", "pacaur", "trizen" or "pikaur". If such a helper
# is already installed on the target host then there is no need to install it
# via this role. In this case "iscsi_archlinux_aur_helper" needs to be 
# commented and this role will skip the installation of an AUR helper.
# The install task picks one of the AUR helper mentioned above (in that order)
# to install the iSCSI packages.
iscsi_archlinux_aur_helper: yay

# While Ansible expects to SSH as root, makepkg or AUR helpers do not allow
# executing operations as root, they fail with "you cannot perform this
# operation as root". It is therefore recommended to have a user, which
# is non-root but has no need for password. If "iscsi_archlinux_aur_helper"
# variable is set it is assumed that the AUR helper user doesn't exist yet
# so it will be created. The user will be part of the "wheel" group.
iscsi_archlinux_aur_helper_user: aur_builder
```

Dependencies
------------

For Archlinux [kewlfft.aur](https://galaxy.ansible.com/kewlfft/aur) Ansible collection is used to 1) install an AUR helper like [yay](https://github.com/Jguer/yay) and 2) to install [targetcli](https://aur.archlinux.org/packages/targetcli-fb/) utility from Archlinux User Repository.

Example Playbook
----------------

```yaml
- hosts: your-host
  become: true
  gather_facts: true
  roles:
    - githubixx.iscsi_target
  vars:
    iscsi_targets:
      - name: "iqn.2021-11.blog.tauceti:{{ ansible_facts['nodename'] }}"
        disks:
          - name: lun_node1
            path: /dev/vdb
            type: block
            lunid: 0
        initiators:
          - name: iqn.2021-07.blog.tauceti:node1
            authentication:
              userid: node1user
              password: node1pw
              userid_mutual: node1sharedkey
              password_mutual: node1sharedsecret
            mapped_luns:
              - mapped_lunid: 0
                lunid: 0
        portals:
          - ip: "0.0.0.0"
```

Testing
-------

This role has a small test setup that is created using [Molecule](https://github.com/ansible-community/molecule), libvirt (vagrant-libvirt) and QEMU/KVM. Please see my blog post [Testing Ansible roles with Molecule, libvirt (vagrant-libvirt) and QEMU/KVM](https://www.tauceti.blog/posts/testing-ansible-roles-with-molecule-libvirt-vagrant-qemu-kvm/) how to setup. The test configuration is [here](https://github.com/githubixx/ansible-role-iscsi_target/tree/master/molecule/kvm).

Afterwards molecule can be executed:

```bash
molecule converge
```

This will setup a few virtual machines (VM) with different supported Linux operating systems and installs `iscsi_target` role.

To clean up run

```bash
molecule destroy
```

License
-------

MIT/BSD

Author Information
------------------

Original author: Ondrej Famera [ansible.targetcli](https://github.com/OndrejHome/ansible.targetcli)  
Additional author: Ricardo Sanchez [ansible-role-iscsi_target](https://github.com/ricsanfre/ansible-role-iscsi_target)  
Additional author (this role version): [https://www.tauceti.blog](http://www.tauceti.blog)
