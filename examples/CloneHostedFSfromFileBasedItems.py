from __future__ import print_function

#
#   This example demonstrates how to copy all Shapefile, File Geodatabase, and SD
#   items that have been published as Hosted Feature Services from a source
#   portal to a target portal.
#
#   Based on the connected user credentials, it queries all these items types and
#   if the item has a reverse relationship with a Feature Service, then the file
#   item will be copied to the source Portal and published as a Hosted Feature Service.
#
#   This script makes some basic assumptions that existing item names and service names
#   do not exist in the target Portal before copying.
#
#   This will not copy/publish Tile Services, Map Services, and other service types
#   at this time if related to an SD file.
#

import sys
import six
from arcgis.gis import *

if six.PY3:
    from urllib.error import URLError
else:
    # unresolved reference in Python3, but should work if running from Python2
    from urllib2 import URLError

# Wrap source GIS connection with error handling to determine why it may fail
try:
    source = GIS("http://portalhostds.ags.esri.com/gis", "sharing1", "secret.pwd")
except URLError as e:
    sys.exit("Invalid portal URL...")
except RuntimeError as e2:
    sys.exit("Invalid Username/password...")

# Wrap target GIS connection with error handling to determine why it may fail
try:
    target = GIS("https://wdctyint000032.esri.com/portal", "portaladmin", "secret.pwd")
except URLError as e:
    sys.exit("Invalid portal URL...")
except RuntimeError as e2:
    sys.exit("Invalid Username/password...")

# Let's make sure the Target Portal supports Hosted Feature Services for publication
props = target.properties
if not props["supportsHostedServices"]:
    sys.exit("Target Portal does not support Hosting services...")


def copy_item(target, owner, folder, item):
    # Item properties we will copy from Source to Target Portals
    ITEM_COPY_PROPERTIES = [
        "title",
        "type",
        "typeKeywords",
        "description",
        "tags",
        "snippet",
        "extent",
        "spatialReference",
        "name",
        "accessInformation",
        "licenseInfo",
        "culture",
        "url",
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        new_item = {}
        for property_name in ITEM_COPY_PROPERTIES:
            new_item[property_name] = item[property_name]

        # We know only file based items are being processed, so we must
        # download them for the item copy
        data_file = item.download(temp_dir)
        thumbnail_file = item.download_thumbnail(temp_dir)
        metadata_file = item.download_metadata(
            temp_dir
        )  # If no metadata, comes back as None
        # Add the item to the target portal
        try:
            dup_item = target.content.add(
                new_item, data_file, thumbnail_file, metadata_file, owner, folder
            )
        except RuntimeError as e2:
            print(e2)
            return None
        return dup_item


usercontent = source.users.me.items()
folders = source.users.me.folders

# Let's handle any items at the root My Contents level first
for item in usercontent:
    if item.type in ["Service Definition", "Shapefile", "File Geodatabase"]:
        relitems = item.related_items("Service2Data", "reverse")
        if len(relitems) == 1:
            # Only handle the case where the related item is a Feature Service.
            # This will avoid Tile Layers, Map Services, etc. related to SD files.
            relitem = relitems[0]
            if relitem.type == "Feature Service":
                print("Attempting to copy and publish {}...".format(item.name))
                # Copy the file based item first
                copied_item = copy_item(target, target.users.me, None, item)
                if copied_item is not None:
                    try:
                        # Now publish the item...
                        print("\tCopied.  Attempting service publishing...")
                        service = copied_item.publish()
                    except:
                        print("\tPublishing error...")
                        continue  # Skip following statements; move on to next item
                    # Finally, update the tags on the Feature Service with tags from the original
                    success = service.update(item_properties={"tags": relitem["tags"]})
                    if success:
                        # if we made it this far, then we can assume everything went smoothly
                        print(
                            "\tSuccessfully transitioned {} to target Portal...\n".format(
                                item.name
                            )
                        )

# Let's handle any items found in any folders.
# This will NOT create new folders in the target Portal user's content.
# It will copy/publish items to the root folder of the user's My Contents.
for folder in folders:
    folderitems = source.users.me.items(folder["title"])
    for item in folderitems:
        if item.type in ["Service Definition", "Shapefile", "File Geodatabase"]:
            relitems = item.related_items("Service2Data", "reverse")
            if len(relitems) == 1:
                # Only handle the case where the related item is a Feature Service.
                # This will avoid Tile Layers, Map Services, etc. related to SD files.
                relitem = relitems[0]
                if relitem.type == "Feature Service":
                    print("Attempting to copy and publish {}...".format(item.name))
                    # Copy the file based item first
                    # Copy to source user's root My Contents folder to avoid if folder name doesn't exist
                    copied_item = copy_item(target, target.users.me, None, item)
                    if copied_item is not None:
                        try:
                            # Now publish the item...
                            print("\tCopied.  Attempting service publishing...")
                            service = copied_item.publish()
                        except:
                            print("\tPublishing error...")
                            continue  # Skip following statements; move on to next item
                        # Finally, update the tags on the Feature Service with tags from the original
                        success = service.update(
                            item_properties={"tags": relitem["tags"]}
                        )
                        if success:
                            # if we made it this far, then we can assume everything went smoothly
                            print(
                                "\tSuccessfully transitioned {} to target Portal...\n".format(
                                    item.name
                                )
                            )
