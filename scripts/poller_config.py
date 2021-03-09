import json
from MediatorFolderMonitor import FolderFetcher
from insite_plugin import InsitePlugin


class Plugin(InsitePlugin):
    def can_group(self):
        return False

    def fetch(self, hosts):

        try:

            self.collector

        except Exception:

            host = hosts[-1]

            params = {
                "host": host,
                "port": "8080",
                "system_name": "MAN_Production",
                "login": {"user": "evertz", "pass": "pharos1"},
            }

            self.collector = FolderFetcher(**params)

        documents = []

        for metrics in self.collector.generate_stats():

            document = {"fields": metrics, "host": metrics["s_host_name"], "name": "folders"}

            documents.append(document)

        return json.dumps(documents)
