import argparse
import datetime
import json
import os
from xml.dom import minidom

import requests


class folder_fetcher:
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

        self.sub = None

        for key, value in kwargs.items():

            if "host" == key and value:
                self.host = value

            if "port" in key and value:
                self.port = value

            if "sub" in key and value:
                self.sub = value

        self.url_get_services = "http://{}:{}/{}".format(
            self.host, self.port, self.get_services_route
        )

        self.catalog_folder_services()

        # resp = self.fetch(self.url_get_services, self.request_services_params)

        # print(resp.toprettyxml())

    def fetch(self, url, params):

        try:

            resp = requests.get(url, params=params, headers={"Accept": "application/xml"})

            resp.close()

            doc = minidom.parseString(str(resp.text))

            return doc

        except Exception as e:
            print(e)
            return None

    def catalog_folder_services(self):
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

            doc = self.fetch(self.url_get_services, self.request_services_params)

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


def main():

    params = {
        "host": "aws-core03.ironmam.mws.disney.com",
        "port": "8080",
        "sub": "../_files/services.xml",
    }

    foldermonitor = folder_fetcher(**params)

    print(json.dumps(foldermonitor.folder_catalog, indent=2))


if __name__ == "__main__":
    # mediator
    main()

