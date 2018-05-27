"""
All lookup tables.
"""
import logging

location = {'beijing': '6', 'ceqa': '12', 'taipei': '13'}

loglevel = {'debug': logging.DEBUG, 'info': logging.INFO,
            'warning': logging.WARNING, 'error': logging.ERROR,
            'critical': logging.CRITICAL}


machine_metainfo_attr = ['make', 'model', 'codename', 'form_factor',
                         'processor', 'video', 'wireless', 'network']

device_audio_attr = ['audio_pciid', 'audio_name']
