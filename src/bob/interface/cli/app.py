from typing import TYPE_CHECKING

import click
import uvloop

from bob.init import initialize
from bob.interface.events.telegram_update_router import TelegramUpdateRouter

if TYPE_CHECKING:
    from bob.application import Application


@click.group
@click.pass_context
def main(context: click.Context) -> None:
    context.obj = initialize()


@main.command
@click.pass_obj
def handle_updates(app: Application) -> None:
    uvloop.run(TelegramUpdateRouter(app).run())
