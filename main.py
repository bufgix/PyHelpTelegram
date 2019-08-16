from telegram.ext import Updater, CommandHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from telegram.bot import Bot
from telegram.parsemode import ParseMode
import textwrap
import logging
import importlib
import re
import sys


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


class HelpBot:
    def __init__(self):
        self.Bot: Bot = None

    def get_buildin_doc(self, method_name: str) -> str:
        return getattr(__builtins__, method_name).__doc__

    def package_import(self, package_name: str) -> str:
        """
            Bu fonksiyon paket ismini tam string şeklinde alır
            Ör:
            package_name = 'package.subpackage.attr'
                            \_____/\_________/ \__/
                           /           |             \
                         /            |                \
            paket ismi(gerkli)    altpaket(eğer varsa)   fonksiyon, sınıf veya degisken

            ve geriye kullanımını döndürür. Eğer None ise bu __doc__'un boş olduğu anlamına
            gelir.
            Hataları ModuleNotFound ile yakalayın.
        """
        modules = [i for i in package_name.split('.') if i]
        if len(modules) <= 1:  # Eğer nokta notasyonu kullanılmadıysa...
            if modules[0] in dir(
                    __builtins__):  # Eğer bir build-in fonksiyonu varsa
                return self.get_buildin_doc(modules[0])
            return importlib.import_module(modules[0]).__doc__
        else:
            package = importlib.import_module('.'.join(modules[:-1]))
            return getattr(package, modules[-1]).__doc__

    def generate_docs_url(self, package_name: str) -> str:
        docs_url = "https://docs.python.org/3/library/{module}.html#{attr}"

        # HARD CODE ALERT !
        modules = [i for i in package_name.split('.') if i]
        if len(modules) <= 1:  # Eğer nokta notasyonu kullanılmadıysa...
            if modules[0] in dir(
                    __builtins__):  # Eğer bir build-in fonksiyonu varsa
                return docs_url.format(module="functions", attr=modules[0])
            return docs_url.format(module=modules[0], attr='')
        else:
            return docs_url.format(module=modules[0], attr='.'.join(modules))

    def py_help(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        match = re.match(r"/pyhelp\s+(.+)", update.message.text)
        if match:
            import_str = match.group(1)
            try:
                doc = self.package_import(import_str)
                if not doc:
                    self.bot.send_message(
                        chat_id,
                        f"No information provided `{import_str}`",
                        parse_mode=ParseMode.MARKDOWN)
                    return

                self.bot.send_message(
                    chat_id,
                    f"```{textwrap.dedent(doc[:300])}[...]``` [Read Mode]({self.generate_docs_url(import_str)}",
                    parse_mode=ParseMode.MARKDOWN)
            except ModuleNotFoundError:
                self.bot.send_message(
                    chat_id,
                    f"Not found `{import_str}`",
                    parse_mode=ParseMode.MARKDOWN)
        else:
            pass

    def start(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        template = textwrap.dedent(f"""
        Python version: `{sys.version}`

        Python docs for Telegram
        """)
        self.bot.send_message(chat_id, template, parse_mode=ParseMode.MARKDOWN)

    def run(self, token: str):
        updater = Updater(token, use_context=True)
        dispatcher = updater.dispatcher
        self.bot = updater.bot
        dispatcher.add_handler(CommandHandler("pyhelp", self.py_help))
        dispatcher.add_handler(CommandHandler("start", self.start))

        # Run bot
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    bot = HelpBot()
    bot.run("~")
    # print(bot.generate_docs_url('argparse.ArgumentParser.parse_args'))
