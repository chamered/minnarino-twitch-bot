from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog
from textual.containers import Horizontal, Vertical
from bot import Bot

class MinnarinoDashboard(App):
    CSS = """
    RichLog {
        padding: 1;
        background: #000000;
    }
    #chat_log {
        width: 50%;
        height: 100%;
        border: solid cyan;
    }
    #right_panel {
        width: 50%;
        height: 100%;
    }
    #bot_log {
        width: 100%;
        height: 70%;
        border: solid violet;
    }
    #system_log {
        width: 100%;
        height: 30%;
        border: solid orange;
    }
    """

    TITLE = "Minnarino Bot - Control Center"
    BINDINGS = [("q", "quit", "Quit Dashboard")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield RichLog(id="chat_log", highlight=False, markup=True, wrap=True)

            with Vertical(id="right_panel"):
                yield RichLog(id="bot_log", highlight=True, markup=True, wrap=True)
                yield RichLog(id="system_log", highlight=True, markup=True, wrap=True)
        yield Footer()
    
    async def on_mount(self) -> None:
        chat_log = self.query_one("#chat_log", RichLog)
        bot_log = self.query_one("#bot_log", RichLog)
        system_log = self.query_one("#system_log", RichLog)
        chat_log.border_title = "CHAT"
        bot_log.border_title = "MINNARINO"
        system_log.border_title = "SYSTEM"
        self.bot = Bot(gui_log_callback=self.route_log)
        self.run_worker(self.bot.start(), exclusive=True)
        self.route_log("[SYSTEM] Dashboard initialized. Bot is starting...")
    
    def route_log(self, message: str) -> None:
        if message.startswith("[cyan]"):
            chat_log = self.query_one("#chat_log", RichLog)
            chat_log.write(message)
        elif message.startswith(">"):
            bot_log = self.query_one("#bot_log", RichLog)
            bot_log.write(message)
        else:
            system_log = self.query_one("#system_log", RichLog)
            system_log.write(message)

if __name__ == "__main__":
    app = MinnarinoDashboard()
    app.run()