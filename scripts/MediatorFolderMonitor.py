import copy
import datetime
import json
import os
from xml.dom import minidom

import requests


class FolderFetcher:
    def __init__(self, **kwargs):

        self.host = None
        self.port = "8080"
        self.get_services_route = "info/scripts/CGItoXML.exe/servicerequest"
        self.folder_catalog = {}

        self.request_services_params = {
            "uniqueid": 0,
            "command": "getservices",
            "noxsl": None,
        }

        self.request_folder_params = {
            "uniqueid": None,
            "command": "GetFolderList",
            "noxsl": None,
        }

        self.sub = None
        self.logon = None
        self.elapse_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        self.headers = {"Accept": "application/xml"}
        self.sys_name = None

        for key, value in kwargs.items():

            if key == "host" and value:
                self.host = value

            if "port" in key and value:
                self.port = value

            if "sub" in key and value:
                self.sub = value

            if "system_name" in key and value:
                self.system_name = value

        if "login" in kwargs.keys():

            self.login_params = {
                "uniqueid": 0,
                "command": "login",
                "noxsl": None,
                "user": kwargs["login"]["user"],
                "pass": kwargs["login"]["pass"],
                "successrequest": "",
            }

            self.logout_params = {
                "uniqueid": 0,
                "command": "logout",
                "noxsl": None,
            }

            self.url_login_service = "http://{}:{}/{}".format(
                self.host, self.port, self.get_services_route
            )

            self.logon = True

        self.url_get_services = "http://{}:{}/{}".format(
            self.host, self.port, self.get_services_route
        )

    def login(self, http_session):

        try:

            resp = http_session.post(
                self.url_login_service,
                data=self.login_params,
                headers={
                    "Accept": "application/xml",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

            if (
                "<Error>Username or password not recognized</Error>" not in resp.text
                or resp.status_code != 200
            ):

                return resp.status_code

        except Exception as e:
            print(e)

        print(resp.status_code)
        print(resp.text)

        return None

    def logout(self, http_session):

        try:

            http_session.get(
                self.url_login_service, params=self.logout_params, headers=self.headers,
            )

        except Exception as e:
            print(e)

    def fetch(self, http_session, url, params):

        try:

            resp = http_session.get(url, params=params, headers=self.headers)

            doc = minidom.parseString(str(resp.text))

            return doc

        except Exception as e:
            print(e)
            return None

    def generate_stats(self):

        with requests.Session() as http_session:

            if self.logon:

                # exit out of function if login failed
                if not self.login(http_session):
                    return None

            diff = datetime.datetime.utcnow() - self.elapse_time

            # refresh the folder catalog if older than 5m
            if diff.total_seconds() > 300:
                self.catalog_folder_services(http_session)

            for _, items in self.folder_catalog.items():

                yield self.fetch_folder(http_session, items)

            if self.logon:
                self.logout(http_session)

    def fetch_folder(self, http_session, folder):
        # recursive function to scan folders by recalling with a childNode
        def folder_scan(dom_obj):

            files = 0
            folders = 0

            # encase there something that isn't a element node
            if dom_obj.nodeType is minidom.Node.ELEMENT_NODE:

                # just get the file count and return right away
                if dom_obj.tagName == "Files":

                    files += int(dom_obj.getAttribute("count"))

                    return files, folders

                # theres probably a folder node
                else:

                    # try to get the count attribute. fail and do nothing if it doesn't exist
                    try:
                        folders += int(dom_obj.getAttribute("count"))

                    except Exception:
                        pass

                    # start iterating through childnodes if there are any
                    for sub_node in dom_obj.childNodes:

                        # try to call back into this function again. otherwise if the return
                        # is null, then continue the iteration. function could return null if dom object
                        # isn't what expected.
                        try:

                            _files, _folders = folder_scan(sub_node)

                            # add the found results to the current stack counters
                            files += _files
                            folders += _folders

                        except Exception:
                            continue

                    # return current stack or everything
                    return files, folders

        # if the unique_id is ready then start the folder collection
        if "i_unique_id" in folder.keys():

            doc = None

            # get a copy folder parameters
            folder_metrics = copy.deepcopy(folder)

            # try to get a file named after the unique id. needs more work...
            if self.sub:

                try:

                    with open(
                        os.getcwd() + "\\_files\\" + str(folder["i_unique_id"]) + ".xml", "r"
                    ) as f:

                        strdoc = f.read()

                        strdoc = strdoc.replace("\n", "")
                        strdoc = strdoc.replace("\r", "")
                        strdoc = strdoc.replace("\t", "")

                        doc = minidom.parseString(strdoc)

                except Exception as e:
                    pass
                    # print(e)

            # get a copy of the request parameters and update the uniqeid with the folder params
            else:

                params = copy.deepcopy(self.request_folder_params)
                params["uniqueid"] = folder["i_unique_id"]

                doc = self.fetch(http_session, self.url_get_services, params)

            # scan the dom if there is a valid minidom object
            if doc:

                # get into the Monitored Folders tree. if it doesn't exist then this returns out
                for folder in doc.getElementsByTagName("MonitoredFolders"):

                    try:

                        folder_count = int(folder.getAttribute("count"))

                        # if there's monitored folders (>0) then begin scanning through each mounts
                        if folder_count > 0:

                            folder_metrics.update(
                                {
                                    "i_count": folder_count,
                                    "i_file_count": 0,
                                    "i_folder_count": 0,
                                    "as_mounts": [],
                                }
                            )

                            # not sure if there could be more than one folder (mount) for a monitored folder service
                            for mount in folder.childNodes:

                                # test if instance is valid element node minidom. otherwise skip.
                                if mount.nodeType is minidom.Node.ELEMENT_NODE:

                                    folder_metrics["as_mounts"].append(mount.getAttribute("path"))

                                    # iterate through each sub node in the mount node regardless what it is
                                    for sub_node in mount.childNodes:

                                        try:

                                            # call the folder_scan which will recursively keep looking for nested folders and files
                                            # add to the count if there's multiple mounts (doubt there is.. but anywhoo)
                                            files, folders = folder_scan(sub_node)

                                            folder_metrics["i_file_count"] += files
                                            folder_metrics["i_folder_count"] += folders

                                        except Exception:
                                            continue

                        else:

                            # just set it to 0 and exit out
                            folder_metrics.update({"i_count": folder_count})

                    except Exception as e:
                        print(e)

            if self.system_name:
                folder_metrics.update({"s_system": self.system_name})

            return folder_metrics

    def catalog_folder_services(self, http_session):
        def get_element(node, name):

            try:
                return node.getElementsByTagName(name)[0].firstChild.data

            except Exception:
                return None

        doc = None

        if self.sub:

            try:

                with open(os.getcwd() + "\\_files\\services.xml", "r") as f:

                    strdoc = f.read()

                    strdoc = strdoc.replace("\n", "")
                    strdoc = strdoc.replace("\r", "")
                    strdoc = strdoc.replace("\t", "")

                    doc = minidom.parseString(strdoc)

            except Exception as e:
                print(e)

        else:

            doc = self.fetch(http_session, self.url_get_services, self.request_services_params)

        if doc:

            for service in doc.getElementsByTagName("ServiceReg"):

                if get_element(service, "Name") == "Folder Monitor":

                    host_ip = get_element(service, "Host")
                    host_name = get_element(service, "HostName")
                    instance = get_element(service, "Instance")
                    unique_id = int(get_element(service, "UniqueID"))

                    self.folder_catalog.update(
                        {
                            instance: {
                                "s_host_ip": host_ip,
                                "s_host_name": host_name,
                                "s_instance": instance,
                                "i_unique_id": unique_id,
                            }
                        }
                    )

            self.elapse_time = datetime.datetime.utcnow()


def main():

    params = {
        "host": "10.127.3.80",
        "port": "8080",
        "login": {"user": "evertz", "pass": "pharos1"},
        "system_name": "MAM_Production",
        # "sub": "../_files/services.xml",
    }

    folder_monitor = FolderFetcher(**params)

    inputQuit = False

    while inputQuit is not "q":

        for metrics in folder_monitor.generate_stats():
            print(metrics)

        print(json.dumps(folder_monitor.folder_catalog, indent=2))

        inputQuit = input("\nType q to quit or just hit enter: ")


if __name__ == "__main__":
    main()
