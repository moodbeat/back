import logging
import re


class RemoveEscapeSequencesFilter(logging.Filter):
    def filter(self, record):
        record.msg = re.sub(r'\x1b[^m]*m', '', record.msg)
        return True
