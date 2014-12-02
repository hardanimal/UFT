#!/usr/bin/env python
# encoding: utf-8
"""Description:
"""

__version__ = "0.1"
__author__ = "@boqiling"

from UFT.backend import load_config, sync_config, load_test_item

test_uri = "sqlite:///C:\\UFT_DB\\pgem_config.db"


#config = load_config(test_uri, partnumber="AGIGA9601-002BCA", revision="04")
#for item in config.testitems:
#    if(item.name == "Charge"):
#        Charge_Option = item
#print Charge_Option.max
#print Charge_Option.misc


if __name__ == "__main__":
    sync_config(test_uri, "./")
    config = load_config(test_uri, partnumber="AGIGA9601-002BCA", revision="04")
    charge_settings = load_test_item(config, "Charge")
    print charge_settings
    print charge_settings["ChargeOption"]
    print charge_settings["max"]
    programming = load_test_item(config, "Program_VPD")
    print programming["File"]
    print programming["stoponfail"]
    print programming["enable"]


    import os
    print os.path.isfile(programming["File"])

