# NetSec-Firewall

Firewall-e is a command-line program destined to help create (or modify) iptables rules tailored to the user's needs.
It currently supports rules for clients or servers, particularily for the following protoocls : https, http, ssh and ftp.

## Installation
The device that will run the application needs :
- python3
- the firewall-e.py file

The device on which the firewall will be deployed needs:
- iptables
- if the firewall should be made permanent (on Debian and Ubuntu) : iptables-persistent

## Use
In a terminal, run firewall-e.py :
```
python3 firewall-e.py
```
This will open the app in the default mode, which allows to create a new set of iptables rules.
Questions will then be displayed, to which a typed 'yes', 'y' or 'no', 'n' should be replied.
After all questions are done, the rules will be saved in a .txt file, and a corresponding .json style is created to be loaded later.

To apply the firewall, the .txt file needs to be moved to the device on which they need to apply, and then activated with :
```
sudo iptables-restore FILE
```

To make the rules persistent you should then also run :
```
sudo /etc/init.d/iptables-persistent save 
```

### Options
Some options are available to specify the app behavior further :
```
--action {create,load}, -a {create,load}
    Choose whether a new set of rules should be created or an old set should be loaded
--file FILE, -f FILE  
    Name of the existing question_name.json file, created by a previous run of the app
--output OUTPUT, -o OUTPUT
    Name of the desired output file in which to store the rules
```
