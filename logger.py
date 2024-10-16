import logging
import sys

format = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

sqlalchemy_logger = logging.getLogger("sqlalchemy")
sqlalchemy_logger.setLevel(logging.DEBUG)

sqlalchemy_file_handler = logging.FileHandler("./tmp/dbLogs.log")
sqlalchemy_file_handler.setFormatter(format)

sqlalchemy_logger.handlers = [sqlalchemy_file_handler]

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)


app_file_handler = logging.FileHandler("./tmp/Logs.log")
app_stream_handler = logging.StreamHandler(sys.stdout)

app_file_handler.setFormatter(format)
app_stream_handler.setFormatter(format)

logger.handlers = [app_file_handler, app_stream_handler]

sqlalchemy_logger.propagate = False
logger.propagate = False
