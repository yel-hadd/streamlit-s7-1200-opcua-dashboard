import sys
import time
from datetime import datetime

sys.path.insert(0, "..")
# os.environ['PYOPCUA_NO_TYPO_CHECK'] = 'True'

import asyncio
import logging

from asyncua import Client, Node, ua
import time

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("asyncua")


class SubscriptionHandler:
    def __init__(self):
        self.monitored_items = {}

    def datachange_notification(self, node: Node, val, data):
        _logger.info("datachange_notification %r %s", node, val)
        # Assuming 'data' contains the monitored item ID or some identifier
        item_id = data.monitored_item.client_handle
        self.monitored_items[item_id] = val


async def main():
    client = Client(url="opc.tcp://192.168.0.1:4840")
    async with client:
        handler = SubscriptionHandler()
        subscription = await client.create_subscription(100, handler)

        ROOT_NODE = client.get_root_node()
        CHILD_NODES = await ROOT_NODE.get_children()
        OBJECTS_NODES_CHILDREN = await CHILD_NODES[0].get_children()
        SERVER_INTERFACES = OBJECTS_NODES_CHILDREN[2]
        SERVER_1 = await SERVER_INTERFACES.get_children()
        SERVER_1 = SERVER_1[0]
        SERVER_1_VARS = await SERVER_1.get_children()
        SERVER_1_VARS = SERVER_1_VARS[1:]

        handler = SubscriptionHandler()
        subscription = await client.create_subscription(100, handler)

        VARIABLES_TO_SUBSCRIBE = []

        for element in SERVER_1_VARS:
            VARIABLES_TO_SUBSCRIBE.append(element)

        # Example of subscribing to a node and storing the monitored item
        node = VARIABLES_TO_SUBSCRIBE[2]
        monitored_item = await subscription.subscribe_data_change(node)
        handler.monitored_items[monitored_item.client_handle] = node

        # Now you can access the latest values through handler.monitored_items
        while True:
            print(handler.monitored_items)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
