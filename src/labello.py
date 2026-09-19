#!/usr/bin/env python3

"""
A web-based service designed to print labels on your Brother QL label printer.
"""

from app import app, config, logger

if __name__ == "__main__":
    logger.info("starting labello webserver")
    app.run(config.server.host, config.server.port)
