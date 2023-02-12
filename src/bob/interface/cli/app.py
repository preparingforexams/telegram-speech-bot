import asyncio

import click
from bob.application import Application
from bob.init import initialize
from bob.interface.events.telegram_update_router import TelegramUpdateRouter


@click.group
@click.pass_context
def main(context: click.Context) -> None:
    context.obj = initialize()


@main.command
@click.pass_obj
def handle_updates(app: Application) -> None:
    asyncio.run(TelegramUpdateRouter(app).run())
