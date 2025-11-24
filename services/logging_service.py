import logging
import sys

class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            super().emit(record)
        except UnicodeEncodeError:
            msg = self.format(record)
            safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
            record.msg = safe_msg
            super().emit(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        SafeStreamHandler(sys.stderr),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('reminderAPP')
