"""
@Time ： 2024-09-16
@Auth ： Adam Lyu
"""
import logging


def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

#
# # Application log
# app_logger = setup_logger('app_logger', 'logs/app.log')
#
# # Audit log
# audit_logger = setup_logger('audit_logger', 'logs/audit.log')
