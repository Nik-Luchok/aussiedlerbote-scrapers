import logging


def log_filtered_out_ticker(domain: str, url: str) -> None:
    """
    Writes into log file ({domain}_filtered_live_tickers.log)
    live ticker article urls that were filtered out
    """
    # custom logger setup and configuration
    ticker_logger = logging.getLogger('ticker_logger')

    # Check if handlers have already been added
    if not ticker_logger.handlers:

        file_handler = logging.FileHandler(f"{domain}_filtered_live_tickers.log")
        formatter = logging.Formatter(fmt='%(asctime)s | %(name)s %(levelname)s | %(message)s',
                                      datefmt='%d/%m/%Y - %H:%M:%S')

        file_handler.setFormatter(formatter)
        ticker_logger.addHandler(file_handler)

        # add line on first running for readability
        ticker_logger.info('------------------')
        
    # logging message
    ticker_logger.info(f"Filtered out ticker. url: {url}")


def _test_log_filtered_out_ticker():
    domain = 'bild'
    log_filtered_out_ticker(domain, 'https://www.bild.de/sport/fussball/fussball/bild-transferticker-84182958.bild.html')


if __name__ == '__main__':
    _test_log_filtered_out_ticker()
