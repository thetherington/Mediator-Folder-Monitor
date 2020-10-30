import datetime
import json
from xml.dom import minidom

import requests


class folder_fetcher:
    def __init__(self, **kwargs):

        self.host = None
        self.port = "8080"
        self.get_services_route = "info/scripts/CGItoXML.exe/servicerequest"

        self.request_services_params = {
            "uniqueid": 0,
            "command": "getservices",
            "noxsl": None,
        }

        for key, value in kwargs.items():

            if "host" == key and value:
                self.host = value

            if "port" in key and value:
                self.port = value

        self.url_get_services = "http://{}:{}/{}".format(
            self.host, self.port, self.get_services_route
        )

        resp = self.fetch(self.url_get_services, self.request_services_params)

        print(resp.toprettyxml())

    def fetch(self, url, params):

        try:

            resp = requests.get(url, params=params, headers={"Accept": "application/xml"})

            resp.close()

            doc = minidom.parseString(str(resp.text))

            return doc

        except Exception:
            return None


def main():

    params = {
        "host": "aws-core03.ironmam.mws.disney.com",
        "port": "8080",
    }

    foldermonitor = folder_fetcher(**params)


if __name__ == "__main__":
    # mediator
    main()

