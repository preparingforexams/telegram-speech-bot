import logging
import signal

from bob.application import Application

_LOG = logging.getLogger(__name__)


class TelegramUpdateRouter:
    def __init__(self, app: Application):
        self.app = app
        self._should_kill = False

    def _on_signal(self, sig: int, _):
        if sig == signal.SIGTERM:
            self._should_kill = True

    async def run(self):
        signal.signal(signal.SIGTERM, self._on_signal)

        async for update in self.app.ports.telegram_queue.subscribe():
            _LOG.info(f"Received update {update}")

            if self._should_kill:
                _LOG.warning("Shutting down because of signal")
                break
