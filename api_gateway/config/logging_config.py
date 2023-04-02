import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler

# Configurez le format de log
log_format = "[%(asctime)s] - OCR_APP - [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"

# Configurez le niveau de log
log_level = logging.DEBUG

# get log directory
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
if not os.path.isfile(os.path.join(log_dir, "gateway.log")):
    open(os.path.join(log_dir, "gateway.log"), "w").close()

# Créez un gestionnaire de fichiers pour enregistrer les logs dans un fichier
file_handler = TimedRotatingFileHandler(os.path.join(log_dir, "gateway.log"), when="midnight")
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(log_format))

# Créez un gestionnaire de flux pour afficher les logs dans la console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(log_level)
stream_handler.setFormatter(logging.Formatter(log_format))

# Configurez le logger par défaut
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[file_handler, stream_handler],
)
