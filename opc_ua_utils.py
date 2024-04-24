import sys
import time
from datetime import datetime

sys.path.insert(0, "..")
# os.environ['PYOPCUA_NO_TYPO_CHECK'] = 'True'

import asyncio
import logging

from asyncua import Client, Node, ua
import time
import sqlite3

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("asyncua")


class SubscriptionHandler:
    """
    The SubscriptionHandler is used to handle the data that is received for the subscription.
    """

    def __init__(self):
        self.conn = sqlite3.connect("data.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.latest_version = {
            "les seconds": None,
            "INTERR_1": None,
            "Clock_5Hz": None,
            "RELAIS_2": None,
            "reset": None,
        }

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS data_changes (
                node_id TEXT,
                value TEXT,
                timestamp TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS latest_values (
                node_id TEXT PRIMARY KEY,
                value TEXT
            )
        """
        )
        self.conn.commit()

    async def datachange_notification(self, node: Node, val, data):
        """
        Callback for asyncua Subscription.
        This method will be called when the Client received a data change message from the Server.
        """
        
        node_id = str(node.nodeid)
        # use node name as an id instead
        node_id = await node.read_display_name()
        node_id = str(node_id.Text)
        value = str(val)
        timestamp = str(datetime.now())
        self.latest_version[f"{node_id}"] = value
        # update latest values
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO latest_values (node_id, value)
            VALUES (?, ?)
        """,
            (node_id, value),
        )
        self.cursor.execute(
            """
            INSERT INTO data_changes (node_id, value, timestamp)
            VALUES (?, ?, ?)
        """,
            (node_id, value, timestamp),
        )
        self.conn.commit()
        # _logger.info("datachange_notification %r %s", node, val)


HANDLER = SubscriptionHandler()


def get_latest_values_from_db(cursor: sqlite3.Cursor) -> dict:
    cursor.execute("SELECT node_id, value FROM latest_values")
    rows = cursor.fetchall()
    latest_values = {}
    for row in rows:
        node_id, value = row
        latest_values[node_id] = value
    return latest_values


async def set_node_value(node: Node, value: ua.Variant, data_type: ua.VariantType):
    """
    Set the value of a node.
    """
    var_value = ua.DataValue(ua.Variant(value, data_type))
    # node_id = node._get_path()
    # fetch node again with new_client
    await node.set_value(var_value)


def get_asyncua_client():
    return Client(url="opc.tcp://192.168.0.1:4840")


async def get_nodes(reset=False):
    client = Client(url="opc.tcp://192.168.0.1:4840")
    async with client:
        # ns=4;i=5
        ROOT_NODE = client.get_root_node()
        CHILD_NODES = await ROOT_NODE.get_children()
        OBJECTS_NODES_CHILDREN = await CHILD_NODES[0].get_children()
        SERVER_INTERFACES = OBJECTS_NODES_CHILDREN[2]
        SERVER_1 = await SERVER_INTERFACES.get_children()
        SERVER_1 = SERVER_1[0]
        SERVER_1_VARS = await SERVER_1.get_children()
        SERVER_1_VARS = SERVER_1_VARS[1:]

        VARIABLES_TO_SUBSCRIBE = []

        for var in SERVER_1_VARS:
            VARIABLES_TO_SUBSCRIBE.append(var)
        # LAST_NODE = VARIABLES_TO_SUBSCRIBE[4]
        # if reset:
        #     set_node_value(LAST_NODE, False, ua.VariantType.Boolean)
        #     import time
        #     time.sleep(10)
        return VARIABLES_TO_SUBSCRIBE


async def listen_for_updates(client, handler, nodes):
    subscription = await client.create_subscription(100, handler)
    await subscription.subscribe_data_change(nodes)


async def main():
    VARS = await get_nodes()
    CLIENT = get_asyncua_client()
    async with CLIENT:
        # await set_node_value(VARS[4], False, ua.VariantType.Boolean)
        await listen_for_updates(CLIENT, HANDLER, VARS)

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
