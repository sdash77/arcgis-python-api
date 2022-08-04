from __future__ import annotations
import argparse
import sys
import logging
import os
import chardet
import csv
import urllib
import unicodedata
import yaml
from arcgis.gis import GIS
from arcgis.gis._impl._con._cert import pfx_to_pem
from itertools import repeat
import concurrent.futures

# global verbose
verbose = False

# For custom log_file path,refer to the line below
log_file_path = "<Enter Desired Log File Path and Comment the Line Below>"
log_file_path = "sample.log"

# Log CLI tool activities
cli_logger = logging.getLogger("CLI_LOG")
cli_logger.setLevel(logging.INFO)

# Log Authentication Activities
auth_logger = logging.getLogger("AUTH_LOG")
auth_logger.setLevel(logging.INFO)

# Log ContentManager activities
content_logger = logging.getLogger("CONTENT_LOG")
content_logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(formatter)

content_logger.addHandler(file_handler)
cli_logger.addHandler(file_handler)
auth_logger.addHandler(file_handler)

parser = argparse.ArgumentParser(description="Add data files")
parser.add_argument(
    "-fp",
    "--file_path",
    type=str,
    metavar="",
    # required=True,
    help="Path of input csv file containing list of Data Files",
)
parser.add_argument(
    "-url",
    "--url",
    type=str,
    metavar="",
    help="URL for Enterprise Users",
)
parser.add_argument(
    "-u",
    "--user",
    type=str,
    metavar="",
    help="Username for the GIS User",
)
parser.add_argument(
    "-p",
    "--password",
    type=str,
    metavar="",
    help="Password for the GIS User",
)
parser.add_argument(
    "-cert",
    "--client_cert",
    type=str,
    metavar="",
    help="Client Certificate for the GIS User",
)
parser.add_argument(
    "-secret",
    "--client_secret",
    type=str,
    metavar="",
    help="Client Secret/Key for the GIS User",
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-b", "--built_in", action="store_true", help="Built In Account Auth"
)
group.add_argument("-pki", "--pki", action="store_true", help="PKI Auth")
group.add_argument("-iwa", "--iwa", action="store_true", help="IWA Auth")

group2 = parser.add_mutually_exclusive_group()
group2.add_argument(
    "-v", "--verbose", action="store_true", help="To see the Traceback call on errors"
)
args = parser.parse_args()


def is_url(url: str) -> bool:
    """
    The `is_url` function returns True if the input string is a valid url otherwise False.
    """
    return urllib.parse.urlparse(url).scheme != ""


def check(data_path: str) -> bool:
    """
    The `check` function returns True if the Driver CSV path is a valid path or a valid URL otherwise False.
    """
    if data_path and os.path.isfile(data_path):
        return True
    elif data_path and is_url(data_path):
        return True
    else:
        cli_logger.error("")
        return False


def input_csv_handler(path: str) -> list[list[dict]] | list:
    """
    The `input_csv_handler` function parses the Driver CSV and returns a list[list[dict]] containing all the information in the CSV
    grouped by item_id.
    """
    if not check(path):
        print("Unsuccessful, please chek logs")
        sys.exit()

    def get_encoding(path: str) -> str:
        """
        The `get_encoding` function returns the most probable encoding of the input CSV file.
        """
        with open(path, "rb") as csv_file:
            encoding = chardet.detect(csv_file.read(10000))["encoding"]
        csv_file.close()
        return encoding

    output = []
    try:
        encoding = get_encoding(path)
        with open(path, encoding=encoding) as csv_file:
            reader = csv.DictReader(csv_file)
            output = [
                {
                    key.strip(): val.strip()
                    if val.strip() != "" or val.strip().lower() != "none"
                    else None
                    for key, val in row.items()
                }
                for row in reader
            ]
    except Exception as e:
        if verbose:
            cli_logger.exception(str(e))
        else:
            cli_logger.error(str(e))
        return output
    else:
        output2 = {}
        for idx in range(len(output)):
            for key in output[idx]:
                if isinstance(output[idx][key], str) and output[idx][key] == "":
                    output[idx][key] = None
            if isinstance(output[idx]["item_properties"], str):
                output[idx]["item_properties"].replace("'", '"')
                output[idx]["item_properties"] = yaml.safe_load(
                    unicodedata.normalize("NFKD", output[idx]["item_properties"])
                )
                # print(output[idx]["item_properties"])
                if output[idx]["item_properties"] != None:
                    for key in output[idx]["item_properties"]:
                        if (
                            isinstance(output[idx]["item_properties"][key], str)
                            and output[idx]["item_properties"][key].lower().strip()
                            == "none"
                        ):
                            output[idx]["item_properties"][key] = None
            item_id = output[idx]["item_id"]
            if item_id != "" or item_id != None:
                if item_id in output2:
                    output2[item_id].append(output[idx])
                else:
                    output2[item_id] = []
                    output2[item_id].append(output[idx])
            else:
                if "NoneType" in output2:
                    output2["NoneType"].append(output[idx])
                else:
                    output2["NoneType"] = []
                    output2["NoneType"].append(output[idx])
        cli_logger.info("Driver csv parsed successfully")
        return list(output2.values())


def built_in(
    url: str | None = None, username: str | None = None, password: str | None = None
) -> tuple[bool, GIS | None]:
    """
    The `built_in` function creates an instance of class:`~arcgis.gis.GIS` using built in authentication
    and returns (True, GIS) if successfully authenticated else (False, None).
    """
    try:
        gis = None
        gis = GIS(url=url, username=username, password=password)
        if gis:
            auth_logger.info("Logged in as- " + gis.properties.user.username)
        else:
            raise Exception
        return (True, gis)
    except Exception as e:
        if verbose:
            if e:
                auth_logger.exception(str(e))
                return (False, str(e))
            else:
                auth_logger.exception("Unable to login, please try again")
                return (False, None)
        else:
            if e:
                auth_logger.error(str(e))
                return (False, None)
            else:
                auth_logger.error("Unable to login, please try again")
                return (False, None)


def pki(
    url: str | None = None,
    client_cert: str | None = None,
    client_secret: str | None = None,
    password: str | None = None,
) -> tuple[bool, GIS | None]:
    """
    The `pki` function creates an instance of class:`~arcgis.gis.GIS` using pki authentication
    and returns (True, GIS) if successfully authenticated else (False, None).
    """
    try:
        gis = None
        if client_cert and password:
            if not os.path.isfile(client_cert):
                auth_logger.error(
                    "Certificate file at {} does not exist.".format(client_cert)
                )
                return (False, None)
            key_file, cert_file = pfx_to_pem(
                pfx_path=client_cert, pfx_password=password
            )
            gis = GIS(
                verify_cert=False,
                url=url,
                key_file=key_file,
                cert_file=cert_file,
            )
        elif client_cert and client_secret:
            if not os.path.isfile(client_cert):
                auth_logger.error(
                    "Certificate file at {} does not exist.".format(client_cert)
                )
                return (False, None)
            if not os.path.isfile(client_secret):
                auth_logger.error(
                    "Key file at {} does not exist.".format(client_secret)
                )
                return (False, None)
            gis = GIS(
                url=url,
                key_file=client_secret,
                cert_file=client_cert,
                verify_cert=False,
            )
        if gis:
            auth_logger.info("Logged in as- " + gis.properties.user.username)
        else:
            raise Exception
        return (True, gis)
    except Exception as e:
        if verbose:
            if e:
                auth_logger.exception(str(e))
                return (False, None)
            else:
                auth_logger.exception("Unable to login, please try again")
                return (False, None)
        else:
            if e:
                auth_logger.error(str(e))
                return (False, None)
            else:
                auth_logger.error("Unable to login, please try again")
                return (False, None)


def iwa(
    url: str | None = None, username: str | None = None, password: str | None = None
) -> tuple[bool, GIS | None]:
    """
    The `iwa` function creates an instance of class:`~arcgis.gis.GIS` using pki authentication
    and returns (True, GIS) if successfully authenticated else (False, None).
    """
    try:
        gis = None
        if username and password:
            gis = GIS(url=url, username=username, password=password)
        else:
            gis = GIS(url=url)
        if gis:
            auth_logger.info("Logged in as- " + gis.properties.user.username)
        else:
            raise Exception
        return (True, gis)
    except Exception as e:
        if verbose:
            if e:
                auth_logger.exception(str(e))
                return (False, None)
            else:
                auth_logger.exception("Unable to login, please try again")
                return (False, None)
        else:
            if e:
                auth_logger.error(str(e))
                return (False, None)
            else:
                auth_logger.error("Unable to login, please try again")
                return (False, None)


def execute(gis: GIS | None, list_of_items: list[dict] | list):
    """
    The 'execute' function iterates the rows of csv in order
    and calls the specific operation for each row.
    """
    idx = 0
    for row in list_of_items:
        idx += 1
        operation = row.get("operation", None)
        if operation == None:
            continue
        elif operation == "add_publish" or operation == "add":
            del row["operation"]
            publish_status = False
            if operation == "add_publish":
                publish_status = True
            item_properties = row.pop("item_properties", None)
            if "upload_size" in row:
                try:
                    row["upload_size"] = float(row["upload_size"])
                except:
                    row["upload_size"] = None
            addItem(
                gis=gis,
                item_data=row,
                item_properties=item_properties,
                publish=publish_status,
            )
        elif operation == "update":
            del row["operation"]
            item_properties = row.pop("item_properties", None)
            updateItem(gis=gis, item_data=row, item_properties=item_properties)
        elif operation == "delete":
            item_id = row.get("item_id", None)
            if item_id == None:
                print(
                    "Unable to delete item at line #{} in the csv, item_id missing".format(
                        str(idx + 1)
                    )
                )
                continue
            deleteItem(gis=gis, item_id=item_id)
        elif operation == "publish":
            item_id = row.get("item_id", None)
            if item_id == None:
                print(
                    "Unable to publish item at line #{} in the csv, item_id missing".format(
                        str(idx + 1)
                    )
                )
                continue
            publishItem(gis=gis, item_id=item_id)
    return


def addItem(
    gis: GIS | None, item_data: dict, item_properties: dict | None, publish=False
):
    file_path = ""
    if item_data["data"] and check(item_data["data"]):
        file_path = item_data["data"]
    else:
        return

    if isinstance(item_data["thumbnail"], str) and not check(item_data["thumbnail"]):
        item_data["thumbnail"] = None

    try:
        item = gis.content.add(
            item_properties=item_properties,
            data=file_path,
            thumbnail=item_data.get("thumbnail", None),
            metadata=item_data.get("metadata", None),
            owner=item_data.get("owner", None),
            folder=item_data.get("folder", None),
            item_id=item_data.get("item_id", None),
            upload_size=item_data.get("upload_size", None),
        )

        if item:
            content_logger.info(
                "Added {} successfully".format(item_properties.get("title", file_path))
            )
            if publish:
                try:
                    item.publish()
                    content_logger.info(
                        "Published {} suvvessfully".format(
                            item_properties.get("title", file_path)
                        )
                    )
                except Exception as e:
                    if verbose:
                        content_logger.exception(
                            "Error publishing item {} , Error - {}".format(
                                item_properties.get("title", file_path), str(e)
                            )
                        )
                    else:
                        content_logger.error(
                            "Error publishing item {} , Error - {}".format(
                                item_properties.get("title", file_path), str(e)
                            )
                        )

        else:
            content_logger.error(
                "Couldn't add {}".format(item_properties.get("title", file_path))
            )
        return
    except Exception as e:
        if verbose:
            content_logger.exception(
                "Error adding item {} , Error - {} ".format(
                    item_properties.get("title", file_path), str(e)
                )
            )
        else:
            content_logger.error(
                "Error adding item {} , Error - {} ".format(
                    item_properties.get("title", file_path), str(e)
                )
            )
        return


def updateItem(gis: GIS | None, item_data: dict, item_properties: dict | None) -> None:
    item_id = item_data.get("item_id", None)
    thumbnail = item_data.get("thumbnail", None)
    if item_id == None:
        content_logger.error(
            "Unable to update item with properties/thumbnail :- {}".format(
                str(item_properties) if item_properties != None else thumbnail
            )
        )
        return
    try:
        item = gis.content.get(item_id)
        if thumbnail != None:
            item.update(thumbnail=thumbnail)
            content_logger.info(
                "Successfully updated thumbnail for item id = {}".format(item_id)
            )
        if item_properties != None:
            item.update(item_properties=item_properties)
            content_logger.info(
                "Successfully updated item properties for item id = {}".format(item_id)
            )
        return
    except Exception as e:
        if verbose:
            content_logger.exception(
                "Item ID = {}, Update error = {}".format(item_id, str(e))
            )
        else:
            content_logger.error(
                "Item ID = {}, Update error = {}".format(item_id, str(e))
            )
        return


def deleteItem(gis: GIS | None, item_id: str) -> None:
    try:
        item = gis.content.get(item_id)
        if item.can_delete:
            gis.content.delete_items([item])
            content_logger.info("Successfuly deleted item {}".format(item_id))
        else:
            content_logger.error("Item id {} cannot be deleted".format(item_id))
        return
    except Exception as e:
        if verbose:
            content_logger.exception(
                "Error occured while deleting item id {} , Error - {}".format(
                    item_id, str(e)
                )
            )
        else:
            content_logger.error(
                "Error occured while deleting item id {} , Error - {}".format(
                    item_id, str(e)
                )
            )
        return


def publishItem(gis: GIS | None, item_id: str) -> None:
    try:
        item = gis.content.get(item_id)
        item.publish()
        content_logger.info("Successfuly published item {}".format(item_id))
        return
    except Exception as e:
        if verbose:
            content_logger.exception(
                "Error occured while publishing item id {} , Error - {}".format(
                    item_id, str(e)
                )
            )
        else:
            content_logger.error(
                "Error occured while publishing item id {} , Error - {}".format(
                    item_id, str(e)
                )
            )
        return


if __name__ == "__main__":

    # Log Type
    verbose = args.verbose

    cli_logger.info("CLI Tool Started")

    # Optional Parameters
    file_path = args.file_path  # required
    url = args.url
    username = args.user
    password = args.password
    client_cert = args.client_cert
    client_secret = args.client_secret

    # Auth Types
    built_in_auth = args.built_in
    pki_auth = args.pki
    iwa_auth = args.iwa

    res = input_csv_handler(file_path)

    gis = None
    auth_status = False

    if built_in_auth:
        auth_status, gis = built_in(url=url, username=username, password=password)
    elif pki_auth:
        auth_status, gis = pki(
            url=url,
            client_cert=client_cert,
            client_secret=client_secret,
            password=password,
        )
    elif iwa_auth:
        auth_status, gis = iwa(url=url, username=username, password=password)
    else:
        auth_logger.error("Please specify auth type and try again.")

    if not auth_status:
        print("Login Unsuccessful, please check logs.")
        sys.exit()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(execute,repeat(gis),res)
    cli_logger.info("CLI tool exited")
    sys.exit()
