from enum import Enum

from OneDrive import *

if __name__ == "__main__":
    onedrive = OneDrive(Stage.DEV)
    items = onedrive.get_items()
    print(type(items))
    for item in items:
        print(item["name"], "| item-id >", item["id"])
