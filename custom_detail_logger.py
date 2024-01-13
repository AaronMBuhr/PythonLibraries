import logging

class YamlMultilineFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)

    def format(self, record):
        original_message = record.msg
        if '\n' in original_message:
            first_line, remaining_lines = original_message.split('\n', 1)
            record.msg = f"{first_line} |\n  " + '\n  '.join(remaining_lines.split('\n'))
        return super().format(record)

    # # Example usage
    # CustomDetailLogger.init_formatter()  # Initialize the formatter once at the start

    # logger = CustomDetailLogger(__name__)
    # logger.debug("Single line debug message")
    # logger.debug("Debug output:\nLine 1 of the output\nLine 2 of the output\nLine 3 of the output")

import logging

class CustomDetailLogger(logging.Logger):
    
    allowed_prefixes = set()

    def __init__(self, name, prefix="", level=logging.NOTSET):
        super().__init__(name, level)
        self.prefix = prefix
        self.detail_level = 0

        # Create a new handler with the specific formatter
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s'))
        # Add the handler to this logger
        self.addHandler(handler)

        # Optionally, set the logger level (if you want a specific level for this logger)
        self.setLevel(level)

    def set_detail_level(self, level):
        if level > 0:
            super().setLevel(logging.DEBUG)
        self.detail_level = level

    @classmethod
    def set_allowed_prefixes(cls, prefixes=""):
        if prefixes == None or prefixes == "None" or prefixes == "none" or prefixes == "NONE":
            prefixes = [ None ]
        if prefixes == "":
            prefixes = []
        cls.allowed_prefixes = set(prefixes)

    @classmethod
    def add_allowed_prefix(cls, prefix):
        cls.allowed_prefixes.add(prefix)

    @classmethod
    def remove_allowed_prefix(cls, prefix):
        cls.allowed_prefixes.discard(prefix)

    @classmethod
    def get_allowed_prefixes(cls):
        return cls.allowed_prefixes

    def _is_prefix_allowed(self):
        # print(f"self.prefix: {self.prefix}, CustomDetailLogger.allowed_prefixes: {CustomDetailLogger.allowed_prefixes}")
        return not CustomDetailLogger.allowed_prefixes \
            or any(allowed_prefix in self.prefix for allowed_prefix in CustomDetailLogger.allowed_prefixes)

    def _log_with_prefix_check(self, level, msg, *args, **kwargs):
        if self._is_prefix_allowed():
            self._log(level, msg, args, kwargs)

    def _format_with_prefix(self, msg, *args, **kwargs):
        return self.prefix + msg, args, kwargs

    def debug(self, msg, *args, **kwargs):
        msg, args, kwargs = self._format_with_prefix(msg, *args, **kwargs)
        self._log_with_prefix_check(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        msg, args, kwargs = self._format_with_prefix(msg, *args, **kwargs)
        self._log_with_prefix_check(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        msg, args, kwargs = self._format_with_prefix(msg, *args, **kwargs)
        self._log_with_prefix_check(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        msg, args, kwargs = self._format_with_prefix(msg, *args, **kwargs)
        self._log_with_prefix_check(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        msg, args, kwargs = self._format_with_prefix(msg, *args, **kwargs)
        self._log_with_prefix_check(logging.CRITICAL, msg, *args, **kwargs)

    def debug1(self, msg, *args, **kwargs):
        if self.detail_level >= 1:
            self.debug(msg, *args, **kwargs)

    def debug2(self, msg, *args, **kwargs):
        if self.detail_level >= 2:
            self.debug(msg, *args, **kwargs)

    def debug3(self, msg, *args, **kwargs):
        if self.detail_level >= 3:
            self.debug(msg, *args, **kwargs)
    
    def debug_pause(self):
        if self.getEffectiveLevel() <= logging.DEBUG:
            input("Press Enter to continue...")

logging.setLoggerClass(CustomDetailLogger)
logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')

# Example usage
# async def cmd_specific_emote(cls, command: str, actor: Actor, input: str):
#     logger = CustomDetailLogger(__name__, prefix="cmd_specific_emote()> ")
#     logger.critical(f"command: {command}, actor.rid: {actor.rid}, input: {input}")
