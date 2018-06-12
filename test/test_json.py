import c3.json.component as c3component
import c3.config as c3config
from c3.helper import compare, convert
from pprint import pprint
from data.cids import cids_before_shrink, cids_after_shrink
from c3.shrink import shrink


configuration = c3config.Configuration.get_instance()


machine_report = {'arch_name': 'amd64',
                  'bios': 'Dell: A01 (Legacy)',
                  'bto_version': '',
                  'buildstamp': '',
                  'canonical_id': '201408-15437',
                  'canonical_label': 'CEB5-E3-CH2',
                  'codename': 'Cedar 15 BDW',
                  'created_at': '2015-10-16T06:29:12.775482',
                  'failed_test_count': 6,
                  'firmware_revision': '0.1',
                  'form_factor': 'Laptop',
                  'id': 106445,
                  'kernel': '3.19.0-30-generic',
                  'kernel_cmdline':
                      'BOOT_IMAGE=/boot/vmlinuz-3.19.0-30-generic '
                      'root=UUID=a165c15f-df27-4e1c-9200-019130889bd9 '
                      'ro quiet splash vt.handoff=7',
                  'make': 'Dell',
                  'memory_swap': '4200591360',
                  'memory_total': '4052176896',
                  'model': 'Inspiron 3543',
                  'network': 'Realtek Semiconductor Co., Ltd. - 10ec:8136',
                  'passed_test_count': 181,
                  'pci_subsystem': '0654',
                  'physical_machine_id': 3147,
                  'processor': 'Intel(R) Core(TM) i7-5###U CPU @ 2.20GHz',
                  'product_name': 'Inspiron 3543',
                  'product_version': 'A01',
                  'release': '14.04.3 LTS',
                  'skipped_test_count': 51,
                  'test_count': 238,
                  'video': 'Intel - 8086:1616',
                  'wireless': 'Atheros Communications - 168c:0036'}


machine_metainfo = {'codename': 'Cedar 15 BDW',
                    'form_factor': 'Laptop',
                    'make': 'Dell',
                    'model': 'Inspiron 3543',
                    'network': 'Realtek Semiconductor Co., Ltd. - 10ec:8136',
                    'processor': 'Intel(R) Core(TM) i7-5###U CPU @ 2.20GHz',
                    'video': 'Intel - 8086:1616',
                    'kernel': '3.19.0-30-generic',
                    'location': 'NA',
                    'wireless': 'Atheros Communications - 168c:0036'}


def compare_shallow_dict(base, target):

    shared_items = set(base.items()) & set(target.items())

    return len(machine_metainfo) == len(shared_items) == len(target)

def test_get_machine_info():

    mm = c3component.get_machine_info(machine_report)

    assert compare_shallow_dict(machine_metainfo, mm)

def test_print_cids():

    configuration.read_configuration('/home/tai271828/work/c3-web-query-working/my_conf.ini')

    cid_objs = convert.dict_to_cid_obj_cids(cids_before_shrink)
    cid_objs_shrank = shrink.get_pool(cid_objs)
    target = convert.cid_obj_to_dict_cids(cid_objs_shrank)

    assert compare.cid_objs(cids_after_shrink, target)
