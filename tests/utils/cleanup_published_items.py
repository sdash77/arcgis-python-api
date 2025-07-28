"""
Go through each org and delete all items that match a certain criteria:

Set 'username' to search for items belonging to a specific user
Set 'tags' to delete only items that match a specific tag
Set 'search_str` to match only items containing a specific string
Set 'day_difference` to find only the items between today's date and n days ago

Use all the above tags together or separately

Set 'test_only' to print out what is to be deleted without deleting



"""

import argparse
from arcgis.gis import GIS, Item
from datetime import datetime, timedelta
from utils._logging import enable_verbose_logging
import logging

enable_verbose_logging(log_level=logging.INFO, log_name="cleanup_published_items.log")


class CleanupTestData:

    username = None

    def __init__(
        self,
        gis,
        tags: str = None,
        search_str: str = None,
        day_difference: int = 7,
        dry_run: bool = True,
    ):
        """
        Get all portal items owned by a specific user and delete them if they are not delete protected and older than a specified number of days.
        :param gis: GIS: The GIS
        :param tags: str: An optional comma separated string of tags to limit the search
        :param search_str: str: An option search string e.g. `title:my_tile` or `type:CSV`
        :param day_difference: int: Difference in days from current date. Default is 90
        :param dry_run: bool: Run the function without deleting the items.
        :return: void
        """
        self.gis = gis
        self.username = self.gis.properties.user["username"]
        self.tags = tags
        self.search_str = search_str
        self.day_difference = day_difference
        self.test_only = dry_run

    def delete_all_items(self):
        print("*************************")
        print(
            f"Delete Items for user {self.username} on {self.gis.url} - Test only: {self.test_only}"
        )
        timestamp_previous_date = (
            datetime.now() - timedelta(days=self.day_difference)
        ).timestamp() * 1000

        query = f"owner:{self.username}"
        if self.tags:
            query = f"owner:{self.username} AND tags:{self.tags}"
        if self.search_str:
            query = f"owner:{self.username} AND {self.search_str}"
        if self.tags and self.search_str:
            query = f"owner:{self.username} AND tags: {self.tags} AND {self.search_str}"
        all_items = self.gis.content.search(
            query=query,
            max_items=10000,
            sort_field="created",
            sort_order="asc",
        )

        item_count = 0
        items_to_process = [
            i for i in all_items if i.modified > timestamp_previous_date
        ]

        print(f"Search found {len(items_to_process)} items...")
        for item in items_to_process:
            # Delete items from the last n days
            print("=====================================")
            print(f"Target {item.title} for delete...")
            if item.can_delete:
                try:
                    related_items = item.related_items("Service2Data", "forward")
                    if len(related_items) > 0:
                        print(
                            f"\t{item.title} has {len(related_items)} related items..."
                        )

                        for rel_item in related_items:
                            item_count += 1
                            if not self.test_only:
                                rel_item.delete(permanent=True)
                                print(
                                    f"\tDeleted related item: {self.print_item_data(rel_item, self.username)}"
                                )
                                item.delete(permanent=True)
                                print(
                                    f"\tDeleted source item: {self.print_item_data(item, self.username)}"
                                )

                    else:
                        if not self.test_only:
                            item.delete(permanent=True)
                            print(
                                f"\tDeleted standalone item: {self.print_item_data(item, self.username)}"
                            )
                        item_count += 1
                except Exception as ex:
                    if "Unable to delete item" in str(
                        ex
                    ) and "(Error Code: 500)" in str(ex):
                        pass
                    print(
                        f"\tFailed to delete item: {self.print_item_data(item, self.username)} -> {str(ex)}"
                    )
        print(f"Processed {item_count} items from {self.gis.url}")
        print("*************************")

    @classmethod
    def print_item_data(cls, item: Item, username: str):
        return f"{item.title} -> {item.type}, {item.itemid}, {username}, {item.url}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gis_profile",
        type=str,
        help="The existing profile name of the target enterprise",
    )
    parser.add_argument(
        "--dry_run",
        type=bool,
        help="Runs the query but will not delete anything",
        default=True,
    )
    parser.add_argument(
        "--day_difference",
        type=int,
        help="How many days from now to query items",
        default="7",
    )

    args = parser.parse_args()
    gis = GIS(profile=args.gis_profile)
    cleanup = CleanupTestData(
        gis=gis, day_difference=args.day_difference, dry_run=args.dry_run
    )
    cleanup.delete_all_items()
