#!/usr/bin/env python3

"""
A web-based service designed to print labels on your Brother QL label printer.
"""

from app import app, logger
import meinheld


if __name__ == '__main__':
    logger.info("starting labello webserver")
    meinheld.listen((app.config['host'], app.config['port']))
    meinheld.run(app)
