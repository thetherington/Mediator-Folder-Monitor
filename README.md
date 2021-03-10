# Mediator Folder Monitor

Mediator Folder Monitoring collection module for the inSITE poller program. Module uses the Mediator Information Center web page to collect all the configure folder monitor services in the entire system.  Module uses the CGItoXML.exe API program for collecting information.

The folder monitor collection module has the below distinct abilities and features:

1. Discovers automatically all the folder monitor servers.
2. Detects if there's folder service with 0 detected folders .
3. Sums up all the number of files and sub folders for a folder service.
4. Refreshes the folder service catalog every 5 minutes for faster processing.

## Minimum Requirements:

- inSITE Version 10.3 and service pack 6
- Python3.7 (_already installed on inSITE machine_)
- Python3.7 xml.dom (_already installed on inSITE machine_)

## Installation:

Installation of the folder monitoring module requires copying the main script into the poller modules folder:

1. Copy __MediatorFolderMonitor.py__ script to the poller python modules folder:

   ```
    cp scripts/MediatorFolderMonitor.py /opt/evertz/insite/parasite/applications/pll-1/data/python/modules/
   ```
2. Restart the poller application

## Configuration:

To configure a poller to use the module start a new python poller configuration outlined below

1. Click the create a custom poller from the poller application settings page.
2. Enter a Name, Summary and Description information.
3. Enter the mediator server running information center in the _Hosts_ tab (can use DNS if it's available).
4. From the _Input_ tab change the _Type_ to __Python__
5. From the _Input_ tab change the _Metric Set Name_ field to __mediator__
6. Select the _Script_ tab, then paste the contents of __scripts/poller_config.py__ into the script panel.
7. Update the parameters "system_name" and "login" with the correct information.

```
            params = {
                "host": host,
                "port": "8080",
                "system_name": "MAN_Production",
                "login": {"user": "evertz", "pass": "pharos1"},
            }

```
   
      Note: If the Mediator Information center does not require a user credentials, remove the "login" parameter from the params dictionary.

8. Save changes, then restart the poller program.

## Testing:

_todo..._

## Sample Data Output:

```
{
 "s_host_ip": "10.207.16.27",
 "s_host_name": "kmtc-comp07",
 "s_instance": "MMRDelivery",
 "i_unique_id": 936775,
 "i_count": 1,
 "i_file_count": 4,
 "i_folder_count": 4,
 "as_mounts": [
  "/mnt/mark50/incoming/ironmam_kmtc_cable"
 ],
 "s_system": "MAN_Production"
}
```

```
{
 "s_host_ip": "10.207.16.28",
 "s_host_name": "kmtc-comp08",
 "s_instance": "paidProgrammingImportPMT",
 "i_unique_id": 936780,
 "i_count": 0,
 "s_system": "MAN_Production"
}
```
