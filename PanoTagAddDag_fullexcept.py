###################################
# Author : Ram Ramachandran
# ETAC Replication
# Create for ETAC-1560
##################################
import sys
import os
import argparse
import logging
import json
import time


curpath = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(curpath, os.pardir)]

from panos import base
from panos.firewall import Firewall
from panos import panorama
from panos import policies
from panos.objects import AddressObject, Tag, AddressGroup
from panos import network
from panos import device

from random import choice
import xml.etree.ElementTree as ET

# Connect to Panorama, create a Tag, Address Group, Address Object on a DeviceGroup_Test
# Push to Panorama and commit-full to specific Device-Group.
# Install pan-os-python library

max_count = 100
def loop_etac1560_test():
    count = 0
    while count < max_count:
        print("Inside Iteration:", count)
        create_pano_objects()
        etac_1560_commit_all()
        rename_pano_address()
        etac_1560_commit_all()
        delete_pano_objects()
        etac_1560_commit_all()
        count += 1
        print("-----------------------")

def etac_1560_commit_all():
    commit_all_pano_dg("PaloAlto-TestGroup")
    commit_all_pano_dg("PaloAlto-TestGroup2")
    commit_all_pano_dg("PaloAlto-TestGroup3")
    time.sleep(180)


def create_pano_objects():
    try:
        active_pano = panorama.Panorama("10.46.33.126","pse-admin","PaloAlto123!")
        DG_Script = panorama.DeviceGroup("PaloAlto-TestGroup")
        active_pano.add(DG_Script)
        active_pano.refresh_system_info()
        count = 0
        while count < max_count:
            tagname    = "TEST_TAG_LIB" + str(count)
            group_name = "TEST_DAG_LIB" + str(count)
            addresses  = ["172.16.10." + str(count) + "/32", "LIB.172.16.10." + str(count) + "_32"]
            color_name = choice(['red', 'green', 'blue', 'copper', 'yellow', 'cyan', 'gold', 'blue gray'])
            print(color_name)
            tag_color = Tag.color_code(color_name)
            tag_object = Tag(name=tagname, color=tag_color)
            active_pano.add(tag_object)
            Tag.refreshall(active_pano)
            tag_object = active_pano.find(tagname, Tag)
            if not tag_object:
                tag_object = Tag(name=tagname, color=tag_color)
                group_object = AddressGroup(name=group_name,dynamic_value="'" + tagname + "'",tag=tagname)
                address_object = AddressObject(name=addresses[1], value=addresses[0], tag=tagname)
                print('Creating Address Objects, DAGs and TAGs', tagname, group_name, addresses[1])
                try:
                    active_pano.add(tag_object)
                    tag_object.create()
                    active_pano.add(group_object)
                    group_object.create()
                    active_pano.add(address_object)
                    address_object.create()
                except:
                    pass
            count += 1
        try:
            jobs_response = active_pano.commit()
        except:
            pass
    except:
        pass
    # if jobs_response:
    #     try:
    #         active_pano.syncjob(jobs_response)
    #     except:
    #         pass

def delete_pano_objects():
    try:
        active_pano = panorama.Panorama("10.46.33.126","pse-admin","PaloAlto123!")
        DG_Script = panorama.DeviceGroup("PaloAlto-TestGroup")
        active_pano.add(DG_Script)
        active_pano.refresh_system_info()
        Tag.refreshall(active_pano)
        AddressObject.refreshall(active_pano)
        AddressGroup.refreshall(active_pano)
        count = 0
        while count < max_count:
            tagname    = "TEST_TAG_LIB" + str(count)
            group_name = "TEST_DAG_LIB" + str(count)
            addresses  = ["172.16.10." + str(count) + "/32", "LIB-172.16.10." + str(count) + "_32", "LIB.172.16.10." + str(count) + "_32"]
            tag_object = Tag(name=tagname)
            active_pano.add(tag_object)
            tag_object = active_pano.find(tagname, Tag)
            if tag_object:
                print('Deleting AddressObjects, DAGs and TAGs -', tagname, addresses[1], group_name)
                address_object = active_pano.find(addresses[1], AddressObject)
                if address_object is None:
                    address_object = active_pano.find(addresses[2], AddressObject)

                group_object = active_pano.find(group_name, AddressGroup)
                try:
                    address_object.delete()
                except AttributeError as error:
                    pass
                try:
                    group_object.delete()
                except AttributeError as error:
                    pass
                try:
                    tag_object.delete()
                except AttributeError as error:
                    pass
            count += 1
        try:
            jobs_response = active_pano.commit()
        except:
            pass
    except:
        pass
    # if jobs_response:
    #     try:
    #         active_pano.syncjob(jobs_response)
    #     except:
    #         pass

def rename_pano_address():
    try:
        active_pano = panorama.Panorama("10.46.33.126","pse-admin","PaloAlto123!")
        DG_Script = panorama.DeviceGroup("PaloAlto-TestGroup")
        active_pano.add(DG_Script)
        active_pano.refresh_system_info()
        AddressObject.refreshall(active_pano)
        count = 0
        while count < max_count:
            try:
                addresses  = ["172.16.10." + str(count) + "/32", "LIB.172.16.10." + str(count) + "_32"]
                address_object = active_pano.find(addresses[1], AddressObject)
                if address_object:
                    print('Renaming AddressObject', addresses[1])
                    address_object.rename("LIB-172.16.10." + str(count) + "_32")
            except:
                pass
            count += 1
        try:
            jobs_response = active_pano.commit()
        except:
            pass
    except:
        pass
    # if jobs_response:
    #     try:
    #         active_pano.syncjob(jobs_response)
    #     except:
    #         pass

def commit_all_pano_dg(dgname, sync=False):
    active_pano = panorama.Panorama("10.46.33.126","pse-admin","PaloAlto123!")
    active_pano.refresh_system_info()
#    active_pano.commit_all(sync=True, devicegroup="PaloAlto-TestGroup")
    active_pano.commit_all(sync, devicegroup=dgname, description="commitAll to " + dgname)

def show_jobs_all():
    active_pano = panorama.Panorama("10.46.33.126","pse-admin","PaloAlto123!")
    element_response = active_pano.op("show jobs all")
    jobs_response = element_response.findall("./result/job")
    pano_clock_response = active_pano.op("show clock")
    print("PAN device time: ", pano_clock_response.find("./result").text)
    for jobs in jobs_response:
        print('-----------------')
        print(ET.tostring(jobs, encoding='unicode'))
        # print("Job ID: ", jobs.find("./id").text)
        # print("Enqueue Time:",jobs.find("./tenq").text)
        # print("Dequeue Time: ", jobs.find("./tdeq").text)
        # print("Type :", jobs.find("./type").text)
        # print("Status: ", jobs.find("./status").text)

def show_system_resources():
    print("-----SHOW SYSTEM RESOURCES---------")
    active_pano = panorama.Panorama("10.46.33.126","pse-admin","PaloAlto123!")
    configd_response = active_pano.op('show system resources')
    print(ET.tostring(configd_response, encoding='unicode'))
    print("------------------------------")

if __name__ == '__main__':
#    loop_main()
#    main()
#    create_pano_objects()
#    rename_pano_address()
#    delete_pano_objects()
#    etac_1560_commit_all()
    loop_etac1560_test()
#    show_jobs_all()
