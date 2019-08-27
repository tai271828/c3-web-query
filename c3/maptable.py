"""
All lookup tables.
"""
import logging

location = {'beijing': '6', 'oem': '8',
            'external-warehouse': '9',
            'mainstream': '10',
            'hwe': '11',
            'ceqa': '12',
            'taipei': '13'}

office = {'taipei-office': ['external-warehouse',
                            'mainstream',
                            'hwe',
                            'ceqa',
                            'taipei'],
          'canonical': location.keys()}

series = {'trusty': ['14.04 LTS',
                     '14.04.1 LTS', '14.04.2 LTS'
                     '14.04.3 LTS', '14.04.4 LTS',
                     '14.04.5 LTS', '14.04.6 LTS']}

status = {'return': 'Returned to partner/customer',
          'with canonical': 'With Canonical'}

loglevel = {'debug': logging.DEBUG, 'info': logging.INFO,
            'warning': logging.WARNING, 'error': logging.ERROR,
            'critical': logging.CRITICAL}


machine_metainfo_attr = ['make', 'model', 'codename', 'form_factor',
                         'processor', 'video', 'wireless', 'network',
                         'kernel',
                         'location']

device_audio_attr = ['audio_pciid', 'audio_name']

comprehensive_cid_attr = machine_metainfo_attr + device_audio_attr

ifamily_series = ['i3', 'i5', 'i7']