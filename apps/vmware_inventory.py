#!/usr/bin/env python
# VMware vSphere Python SDK
# Copyright (c) 2008-2021 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program for listing the VMs on an ESX / vCenter host
"""

import csv
import os
import re
import sys
from pyVmomi import vmodl, vim
from apps.tools import cli, service_instance

from oslo_config import cfg


CONF = cfg.CONF
def vm_info_for_tenant_mapping(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    summary = virtual_machine.summary
    annotation = summary.config.annotation

    ip_address = None
    vmware_tools = None
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
    parent = virtual_machine.parent
    pstack = []
    while parent:
        pstack.append(parent.name)
        parent = parent.parent
    pstack.reverse()
    if pstack:
        folder_path = os.path.join(*pstack)
    else:
        folder_path = "NoPath"
    question = None
    if summary.runtime.question is not None:
        question = summary.runtime.question.text

    vmdetails = {
          "Name": summary.config.name,
          "Template": summary.config.template,
          "Datastore Path": summary.config.vmPathName,
          "Guest": summary.config.guestFullName,
          "Instance UUID": summary.config.instanceUuid,
          "Bios UUID": summary.config.uuid,
          "Annotation": annotation,
          "State": summary.runtime.powerState,
          "VMware-tools": tools_version,
          "IP": ip_address,
          "Question": question,
          "VM Path": folder_path,
          "Tenant": "Domain/Project",
    }

    with open('vminventory.csv', 'a+', newline='') as csvfile:
        fieldnames = vmdetails.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(vmdetails)


def vm_info_for_flavor_creation(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    summary = virtual_machine.summary
    annotation = summary.config.annotation

    try:
        memory = int(summary.config.memorySizeMB /1024 if summary.config.memorySizeMB else 8)
        cpus = int(summary.config.numCpu if summary.config.numCpu else 2)
        nics = int(summary.config.numEthernetCards if summary.config.numEthernetCards else 1)
        numdisk = int(summary.config.numVirtualDisks if summary.config.numVirtualDisks else 1)
        rootdisksize = int(virtual_machine.storage.perDatastoreUsage[0].committed / 1024 / 1024 / 1024)
    except:
        import pdb;pdb.set_trace()

    vmdetails = {
          "Name": summary.config.name,
          "Guest": summary.config.guestFullName,
          "Instance UUID": summary.config.instanceUuid,
          "Annotation": annotation,
          "Memory": memory,
          "CPUs": cpus,
          "NICs": nics,
          "Disks": numdisk,
          "RootDiskSize": rootdisksize,
    }

    with open('vmflavors.csv', 'a+', newline='') as csvfile:
        fieldnames = vmdetails.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(vmdetails)


def discover_vcenter_networks():
    sys.argv = sys.argv[0:1]
    sys.argv += ["-s", CONF.vcenter.host, "-u", CONF.vcenter.admin, "-p", CONF.vcenter.password]

    if not CONF.vcenter.ssl_verify:
       sys.argv.append("-nossl")

    parser = cli.Parser()
    parser.add_custom_argument('-f', '--find', required=False,
                               action='store', help='String to match VM names')
    args = parser.get_args()
    si = service_instance.connect(args)
    content = si.RetrieveContent()

    with open('vmnetworks.csv', 'w', newline='') as csvfile:
        fieldnames = [ "Network Name", "VM Name", "VM Instance UUID"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

    network_view = content.viewManager.CreateContainerView(
        content.rootFolder,
        [vim.Network],
        True)
    networks = list(network_view.view)
    network_view.Destroy()

    with open('vmnetworks.csv', 'a+', newline='') as csvfile:
        network_list = []
        for n in networks:
            for v in n.vm:
                network_details = {'Network Name': n.name,
                                   'VM Name': v.summary.config.name,
                                   'VM Instance UUID': v.summary.config.instanceUuid}
                network_list.append(network_details)
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(network_details)

    return network_list


def discover_vcenter_vms():
    """
    Simple command-line program for listing the virtual machines on a system.
    """

    sys.argv = sys.argv[0:1]
    sys.argv += ["-s", CONF.vcenter.host, "-u", CONF.vcenter.admin, "-p", CONF.vcenter.password]

    if not CONF.vcenter.ssl_verify:
       sys.argv.append("-nossl")

    parser = cli.Parser()
    parser.add_custom_argument('-f', '--find', required=False,
                               action='store', help='String to match VM names')
    args = parser.get_args()
    si = service_instance.connect(args)

    try:
        with open('vminventory.csv', 'w', newline='') as csvfile:
            fieldnames = ["Name", "Template", "Datastore Path", "Guest", "Instance UUID", "Bios UUID",
                          "Annotation", "State", "VMware-tools", "IP", "Question", "VM Path", "Tenant"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

        with open('vmflavors.csv', 'w', newline='') as csvfile:
            fieldnames = [ "Name", "Guest", "Instance UUID", "Annotation", "Memory", 
                           "CPUs", "NICs", "Disks", "RootDiskSize"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()


        content = si.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        view_type = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        container_view = content.viewManager.CreateContainerView(
            container, view_type, recursive)

        children = container_view.view
        if args.find is not None:
            pat = re.compile(args.find, re.IGNORECASE)
        for child in children:
            if args.find is None or \
                 pat.search(child.summary.config.name) is not None:
                vm_info_for_tenant_mapping(child)
                vm_info_for_flavor_creation(child)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    discover_vcenter_vms()
    discover_vcenter_networks()
