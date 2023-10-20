from astropy import config as _config

__all__ = ["conf", "Conf"]


class Conf(_config.ConfigNamespace):
    """
    Configuration parameters for `astroquery.gmeini.Observations`.
    """
    GOA_SERVER = _config.ConfigItem('https://archive.gemini.edu', 'URL for GOA server.')
    GOA_TIMEOUT = _config.ConfigItem(5, 'Time limit for connecting to GOA server.')
    GOA_RADIUS = _config.ConfigItem("0.3 deg", 'Default query radius if not provided.')


conf = Conf()
