"""
Handling csv.
"""
import csv
import logging


logger = logging.getLogger('c3_web_query')


FIELDNAMES = ['CID',
              'Vendor', 'Model', 'Code Name', 'Form',
              'CPU', 'GPU',
              'Wireless', 'Ethernet',
              'Audio ID', 'Audio Name',
              'Unique Label']


def generate_csv_row(cid, writer):
    if cid:
        try:
            writer.writerow({'CID': cid.cid,
                             # 'Release': cid.info_release,
                             # 'Level': info_level,
                             # 'Location': location,
                             'Vendor': cid.make,
                             'Model': cid.model,
                             'Code Name': cid.codename,
                             'Form': cid.form_factor,
                             'CPU': cid.processor,
                             'GPU': cid.video,
                             'Wireless': cid.wireless,
                             'Ethernet': cid.network,
                             'Audio ID': cid.audio_pciid,
                             'Audio Name': cid.audio_name,
                             'Unique Label': cid.unique_label
                             })
        except AttributeError:
            writer.writerow({'CID': cid.cid,
                             # 'Release': cid.info_release,
                             # 'Level': info_level,
                             # 'Location': location,
                             'Vendor': cid.make,
                             'Model': cid.model,
                             'Code Name': cid.codename,
                             'Form': cid.form_factor,
                             'CPU': cid.processor,
                             'GPU': cid.video,
                             'Wireless': cid.wireless,
                             'Ethernet': cid.network,
                             'Audio ID': cid.audio_pciid,
                             'Audio Name': cid.audio_name
                             })
    else:
        logger.warning("No data for {}".format(cid))
        writer.writerow({'CID': cid,
                         'Release': ""})


def generate_csv(cids, csv_file):
    """
    Generate CSV with name csv_file by cid objects

    :param cids: cid objects in list
    :param csv_file: output csv file
    :return: None
    """
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for cid in cids:
            generate_csv_row(cid, writer)


