# Author: Savindi Wijenayaka
# Date: 13.07.2021

import logging

import azure.durable_functions as df


def entity_function(context: df.DurableEntityContext):
    """A Scoreboard Durable Entity. A simple example of a Durable Entity that implements
    a score keeping functionality.

    Args:
        context (df.DurableEntityContext): The Durable Entity context, which exports an 
        API for implementing durable entities.
    """
    current_value = context.get_state(lambda: {"total_combos": 0, "total_wins": 0})
    operation = context.operation_name
    logging.info(f"current value is: {current_value}")
    if operation == "add":
        data = context.get_input()
        current_value["total_combos"] += data["combos_executed"]
        current_value["total_wins"] += data["win"]
        context.set_state(current_value)
    elif operation == "reset":
        current_value = None
        context.set_state(current_value)
    elif operation == "get":
        context.set_result(current_value)


main = df.Entity.create(entity_function)
