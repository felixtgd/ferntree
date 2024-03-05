# DEMKit software
# Copyright (C) 2020 CAES and MOR Groups, University of Twente, Enschede, The Netherlands

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON
# INFRINGEMENT; IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY
# CLAIM, DAMAGES OR ANY OTHER LIABILITY ARISING FROM OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE THEREOF.


# Permission is hereby granted, non-exclusive and free of charge, to any person,
# obtaining a copy of the DEMKit-software and associated documentation files,
# to use the Software for NON-COMMERCIAL SCIENTIFIC PURPOSES only,
# subject to the conditions mentioned in the DEMKit License:

# You should have received a copy of the DEMKit License
# along with this program.  If not, contact us via email:
# demgroup-eemcs@utwente.nl.

# This file is a template to setup DEMKit
# It is important to modify appropriate lines for your system
# Each config item should only appear once, comment the others
# Rename this file to userconf.py

demCfg = {}

# ENVIRONEMNT PARAMETERS
# Modify and adapt the following items

# DSM platform scripts location
demCfg['env'] = {}

# Uncomment and modify one of the following lines
# demCfg['env']['path'] = 'C:/users/yourname/demkitsim/demkit/components/'				# windows
# demCfg['env']['path'] = '/home/user/demkit/components/'			                    # linux
demCfg['env']['path'] = '/Users/felixtangerding/demkitsim/demkit/components/'         # Mac OS X

# User models location
demCfg['workspace']= {}

# Uncomment and modify one of the following lines
# demCfg['workspace']['path'] = 'C:/users/yourname/demkitsim/workspace/example/'        # windows
# demCfg['workspace']['path']= '/home/user/python/workspace/example/'	                 # linux
demCfg['workspace']['path'] = '/Users/felixtangerding/demkitsim/workspace/'            # Mac OS X


# Database settings
demCfg['db'] = {}

#Influxdb
demCfg['db']['influx'] = {}
demCfg['db']['influx']['address'] = "http://localhost"	# Address of the Influx instance
demCfg['db']['influx']['port'] = "8086"					# Port number of the Influx instance
demCfg['db']['influx']['dbname'] = "dem"				# Database name to writ to

# Preparation for Influx 2.0
demCfg['db']['influx']['username'] = "demkit"			# Username of Influx instance
demCfg['db']['influx']['password'] = "WZ5LE3nblOQwpWHrr3m5"					# Password for Influx
demCfg['db']['influx']['token'] = "-WF-JsrugNAZbl4mZJrfT3H6GNXdtNrRWXM-yzuECUJv8XiZqdan0tGq3MFnaEzDRIodcit3Sg0Qh6UiEKZsgg=="


# Variable output for logs ans backups (stored within the workspace folder of a model by default)
# Do not forget the traling slash!
demCfg['var'] = {}
demCfg['var']['backup'] = "var/backup/"
demCfg['var']['databasebackup'] = "var/backup/database/"
demCfg['var']['log'] = "var/log/"



# Timezone information
from pytz import timezone
demCfg['timezonestr'] = 'Europe/Amsterdam'
demCfg['timezone'] = timezone(demCfg['timezonestr'])




# OPTIONAL SETTINGS
# These settings are only required for certain cases and normally can remain unchanged

# Socket path for networked configurations
demCfg['network'] = {}
demCfg['network']['sockPath'] = 'ipc:///home/user/python/'			#linux

#Smart house config
demCfg['smarthouse'] = {}
demCfg['smarthouse']['usb'] = '/dev/ttyACM0'




# STATIC SETTINGS
# You should not modify lines below

# Version control, this config is valid for V4 of DEMKit
demCfg['ver'] = 4.1
