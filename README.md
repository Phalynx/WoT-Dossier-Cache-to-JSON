World of Tanks Dossier Cache to JSON 
==============================================================
Version v8.10


# About Author
* Marius Czyz aka Phalynx
* Contact: marius.czyz@gmail.com


# Demo Systems:
* WoT Performance Analyzer Charts (Online) http://www.vbaddict.net
* WOT Statistics (Offline) http://www.saais.co.za/


# WoT Developer Wiki 
* More information regarding the file structure on the Developer Wiki:
* http://www.vbaddict.net/content/10-WoT-Developer-Wiki


# Supported Versions
* WoT 0.6.x, 0.7.1.x, 0.7.2.x, 0.7.3.x (dossier version 18)
* Wot 0.7.4.x, 0.7.5.x (dossier version 20)
* WoT 0.8.0.x, 0.8.1.x (dossier version 22)
* WoT 0.8.2.x (dossier version 24)
* WoT 0.8.3.x (dossier version 26)
* WoT 0.8.4.x, 0.8.5.x (dossier version 27)
* WoT 0.8.6.x, 0.8.7.x (dossier version 28)
* WoT 0.8.8.x (dossier version 29)
* WoT 0.8.9.x, 0.8.10.x (dossier version 65)


# Contributors WoTDC2J.py
* Phalynx
* Gottzilla
* NJSaaiman



# Usage
* wotdc2j.py <dossier.dat> [rfks]

## Parameters
* -f - By setting f the JSON will be formatted for better human readability
* -r - By setting r the JSON will contain all fields with their values and recognized names
* -k - By setting k the JSON will not contain Kills/Frags
* -s - By setting s the JSON will not include unix timestamp of creation as it is useless for calculation of checksum



## Example
* python.exe wotdc2j.py dossier.dat -f -r
