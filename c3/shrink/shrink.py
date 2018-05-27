import c3.config
import logging


logger = logging.getLogger('c3_web_query')


def get_pool(cid_objs):
    conf_singlet = c3.config.Configuration.get_instance()
    flag_all = conf_singlet.config['SHRINK'].getboolean('all')

    device_categories = ['make', 'model', 'codename', 'form_factor',
                         'processor', 'video', 'wireless', 'network',
                         'audio_pciid', 'audio_name']

    if not flag_all:
        for category in device_categories:
            if conf_singlet.config['SHRINK'].getboolean(category) is None:
                device_categories.remove(category)
                logger.warning("No such category %s" % category)
