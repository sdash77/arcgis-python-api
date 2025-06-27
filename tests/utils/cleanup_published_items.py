"""
Go through each org and delete all items that match a certain criteria:

Set 'username' to search for items belonging to a specific user
Set 'tags' to delete only items that match a specific tag
Set 'search_str` to match only items containing a specific string
Set 'day_difference` to find only the items between today's date and n days ago

Use all the above tags together or separately

Set 'test_only' to print out what is to be deleted without deleting



"""

from arcgis.gis import GIS
from datetime import datetime, timedelta


def delete_all_items(
    gis: GIS,
    username: str = "arcgis_python",
    tags: str = None,
    search_str: str = None,
    day_difference: int = 90,
    test_only=True,
):
    """
    Get all portal items owned by a specific user and delete them if they are not delete protected and older than a specified number of days.
    :param gis: GIS: The GIS
    :param username: str: The name of the user whose items should be deleted: Default is arcgis_python
    :param tags: str: An optional comma separated string of tags to limit the search
    :param search_str: str: An option search string e.g. `title:my_tile` or `type:CSV`
    :param day_difference: int: Difference in days from current date. Default is 90
    :param test_only: bool: Run the function without deleting the items.
    :return: void
    """
    timestamp_previous_date = (
        datetime.now() - timedelta(days=day_difference)
    ).timestamp() * 1000

    query = f"owner:{username}"
    if tags:
        query = f"owner:{username} AND tags:{tags}"
    if search_str:
        query = f"owner:{username} AND {search_str}"
    if tags and search_str:
        query = f"owner:{username} AND tags: {tags} AND {search_str}"
    all_items = gis.content.search(
        query=query,
        max_items=10000,
        sort_field="created",
        sort_order="asc",
    )
    item_count = 0
    for item in all_items:
        # Delete items from the last n days
        if item.modified > timestamp_previous_date:
            if item.can_delete:
                print(f"Deleting {item.title}")
                try:
                    source_item = item.related_items("Service2Data", "forward")[0]
                    if source_item:
                        if not test_only:
                            source_item.delete(permanent=True)
                            item.delete(permanent=True)
                        print(f"\tDeleted source item: {item.title}")
                        item_count += 1
                except IndexError as ie:
                    try:
                        if not test_only:
                            item.delete(permanent=True)
                        print(f"\tDeleted item: {item.title}")
                        item_count += 1
                    except Exception as ex:
                        if "Unable to delete item" in str(
                            ex
                        ) and "(Error Code: 500)" in str(ex):
                            pass
                        print(ex)
                except Exception as ex:
                    print(f"\tFailed to delete item: {item} -> {str(ex)}")
    print(f"Deleted {item_count} items from {gis.url}")


if __name__ == "__main__":
    gis_agol = GIS(
        url="https://geosaurus.maps.arcgis.com/",
        username="arcgispyapibot",
        password="geosaurus_automation123",
    )
    gis_ent = GIS(
        url="https://pythonapitestnb.dev.geocloud.com/portal",
        username="arcgispyapibot",
        password="geosaurus_automation123",
        verify_cert=False,
    )

    print("Delete Items from geosaurus.maps.arcgis.com")
    delete_all_items(gis_agol, day_difference=7, test_only=True)
    print("Delete Items from pythonapitestnb.dev.geocloud.com")
    delete_all_items(gis_ent, day_difference=7, test_only=True)
