"""
Language Server Logger implementation for solidlsp.
"""

import logging


class LanguageServerLogger:
    """
    Simple logger implementation for language servers.
    """

    def __init__(self, name: str = "LanguageServer"):
        self.logger = logging.getLogger(name)

    def log(self, message: str, level: int = logging.INFO) -> None:
        """
        Log a message with the specified level.
        
        :param message: The message to log
        :param level: The logging level
        """
        self.logger.log(level, message)