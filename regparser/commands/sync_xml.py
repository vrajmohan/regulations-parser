import click
import logging

from regparser.index.xml_sync import sync

logger = logging.getLogger(__name__)


@click.command()
@click.option('--xml-ttl', type=int, default=60*60,
              help='Time to cache XML downloads, in seconds')
def sync_xml(xml_ttl):
    """Synchronize modified XML. Checkout/pull down the latest modified XML
    files. If one has been modified, it will notify later steps that they need
    to be rebuilt"""
    logger.info("Syncing XML")
    sync(xml_ttl)
