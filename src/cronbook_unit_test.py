# cronbook_unit_test.py
# Britton Fraley
# 2016-04-10

# ------------------------------------------------------------------------------
# This script tests the utility and data set oriented functions of cronbook.py
# ------------------------------------------------------------------------------

import os
import tempfile
import cronbook
import unittest

class TestUtilityFunctions(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_util_is_int(self):

        s_bad_1 = ''
        s_bad_2 = '&'
        s_bad_3 = 'a'
        s_bad_4 = 'ab'
        s_bad_5 = '0ab'
        s_bad_6 = 'ab0'
        s_bad_7 = '1 ab'
        s_bad_8 = 'ab 1'
        s_bad_9 = '1 2'
        s_good_1 = '1'
        s_good_2 = '10'
        s_good_3 = '1000000'

        self.assertFalse( cronbook.util_is_int(s_bad_1) )
        self.assertFalse( cronbook.util_is_int(s_bad_2) )
        self.assertFalse( cronbook.util_is_int(s_bad_3) )
        self.assertFalse( cronbook.util_is_int(s_bad_4) )
        self.assertFalse( cronbook.util_is_int(s_bad_5) )
        self.assertFalse( cronbook.util_is_int(s_bad_6) )
        self.assertFalse( cronbook.util_is_int(s_bad_7) )
        self.assertFalse( cronbook.util_is_int(s_bad_8) )
        self.assertFalse( cronbook.util_is_int(s_bad_9) )
        self.assertTrue( cronbook.util_is_int(s_good_1) )
        self.assertTrue( cronbook.util_is_int(s_good_2) )
        self.assertTrue( cronbook.util_is_int(s_good_3) )

    def test_util_json_bad(self):

        # document construction
        json_bad_1 = ''
        json_bad_2 = '{}'
        json_bad_3 = '/0'
        json_bad_4 = '[{ "dataset" : "test", "keys" : ["key_1"], "values" : [ [ "value_1" ] ] }]'

        # missing elements
        json_bad_5 = '{ "keys" : ["key_1"], "values" : [ [ "value_1" ] ] }'
        json_bad_6 = '{ "dataset" : "test", "values" : [ [ "value_1" ] ] }'
        json_bad_7 = '{ "dataset" : "test", "keys" : ["key_1"] }'

        # incorrect no of elements
        json_bad_8 = '{ "dataset" : "test", "keys" : ["key_1", "key_2"], "values" : [ [ "value_1" ] ] }'
        json_bad_9 = '{ "dataset" : "test", "keys" : ["key_1"], "values" : [ [ "value_1", "value_2" ] ] }'

        # empty elements
        json_bad_10 = '{ "dataset" : "", "keys" : ["key_1"], "values" : [ [ "value_1" ] ] }'
        json_bad_11 = '{ "dataset" : " ", "keys" : ["key_1"], "values" : [ [ "value_1" ] ] }'

        json_good = '{ "dataset" : "test", "keys" : ["key_1"], "values" : [ [ "value_1" ] ] }'

        self.assertTrue( cronbook.util_json_bad(json_bad_1) )
        self.assertTrue( cronbook.util_json_bad(json_bad_2) )
        self.assertTrue( cronbook.util_json_bad(json_bad_3) )
        self.assertTrue( cronbook.util_json_bad(json_bad_4) )
        self.assertTrue( cronbook.util_json_bad(json_bad_5) )
        self.assertTrue( cronbook.util_json_bad(json_bad_6) )
        self.assertTrue( cronbook.util_json_bad(json_bad_7) )
        self.assertTrue( cronbook.util_json_bad(json_bad_8) )
        self.assertTrue( cronbook.util_json_bad(json_bad_9) )
        self.assertTrue( cronbook.util_json_bad(json_bad_10) )
        self.assertTrue( cronbook.util_json_bad(json_bad_11) )
        self.assertFalse( cronbook.util_json_bad(json_good) )

    def test_util_key_bad(self):

        keys_bad_1 = [cronbook.g_key_name_timestamp, 'key_1', 'key_2']
        keys_bad_2 = ['key_1', 'key_2', 'key_3', 'key_1']
        keys_bad_3 = ['', 'key_2', 'key_3', 'key_1']
        keys_bad_4 = [' ', 'key_2', 'key_3', 'key_1']
        keys_good_1 = [cronbook.g_key_name_unixtime, 'key_1', 'key_2']
        keys_good_2 = [cronbook.g_key_name_unixtime, 'key_1', 'key_2']

        self.assertTrue( cronbook.util_key_bad(keys_bad_1) )
        self.assertTrue( cronbook.util_key_bad(keys_bad_2) )
        self.assertTrue( cronbook.util_key_bad(keys_bad_3) )
        self.assertTrue( cronbook.util_key_bad(keys_bad_4) )

        self.assertFalse( cronbook.util_key_bad(keys_good_1) )
        self.assertFalse( cronbook.util_key_bad(keys_good_2) )

    def test_util_key_exists(self):

        keys = ['key_1', 'key_2', 'key_3']
        key_bad = 'key_4'
        key_good = 'key_1'

        self.assertFalse( cronbook.util_key_exists(keys, key_bad) )
        self.assertTrue( cronbook.util_key_exists(keys, key_good) )

    def test_util_key_index(self):

        keys = ['key_1', 'key_2', 'key_3']
        key_1 = 'key_4'
        key_index_1 = -1
        key_2 = 'key_1'
        key_index_2 = 0
        key_3 = 'key_3'
        key_index_3 = 2

        self.assertEqual( cronbook.util_key_index(keys, key_1) , key_index_1)
        self.assertEqual( cronbook.util_key_index(keys, key_2) , key_index_2)
        self.assertEqual( cronbook.util_key_index(keys, key_3) , key_index_3)

    def test_util_key_new(self):

        schema = ['key_1', 'key_2', 'key_3']
        keys_1 = ['key_1', 'key_2', 'key_3']
        keys_new_1 = []
        keys_2 = ['key_1', 'key_2', 'key_3', 'key_4']
        keys_new_2 = ['key_4']

        self.assertEqual( cronbook.util_key_new(schema, keys_1), keys_new_1)
        self.assertEqual( cronbook.util_key_new(schema, keys_2), keys_new_2)

    def test_util_keys_values_add_time(self):

        keys = ['key_1', 'key_2', cronbook.g_key_name_unixtime]
        values = [['value_1', 'value_2', '0']]
        keys_new = [cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp, 'key_1', 'key_2']
        values_new = [['0', cronbook.util_timestamp_format(0), 'value_1', 'value_2']]

        cronbook.util_keys_values_add_time(keys, values)

        self.assertEqual(keys, keys_new)
        self.assertEqual(values, values_new)

    # uncertain how to test these
    #def test_util_timestamp(self):
    #def test_util_timestamp_format(self):
    #def test_util_timestamp_unix(self):

    def test_util_values_clean(self):

        before_escape_1 = ['embedded 	tab']
        after_escape_1 = ['embedded \\ttab']
        before_escape_2 = ['embedded \nnewline']
        after_escape_2 = ['embedded \\nnewline']
        before_utf8_1 = ['abcdefghijk\xa0']
        after_utf8_1 = ['abcdefghijk']

        self.assertEqual( cronbook.util_values_clean(before_escape_1), after_escape_1)
        self.assertEqual( cronbook.util_values_clean(before_escape_2), after_escape_2)
        self.assertEqual( cronbook.util_values_clean(before_utf8_1), after_utf8_1)

    def test_util_values_order(self):

        schema = [cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp, 'key_1', 'key_2']
        keys = ['key_1', 'key_2', cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp]
        values = ['value_1', 'value_2', '0', cronbook.util_timestamp_format(0)]
        values_ordered = ['0', cronbook.util_timestamp_format(0), 'value_1', 'value_2']

        t = cronbook.util_values_order(schema, keys, values)

        self.assertEqual(values_ordered, t)


class TestDatasetFunctions(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_ds_create(self):

        t = tempfile.NamedTemporaryFile()

        schema = [cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp, 'key_1', 'key_2']
        schema_representation = 'unixtime|timestamp|key_1|key_2\n'

        cronbook.ds_create(t, schema)
        t.seek(0)
        content = t.read()

        self.assertEqual(schema_representation, content)

        t.close()

        with self.assertRaises(cronbook.DiskError):
            cronbook.ds_create(t, schema)

    def test_ds_exists(self):

        t = tempfile.NamedTemporaryFile()
        self.assertTrue( cronbook.ds_exists(t.name) )
        t.close()

    def test_ds_filename(self):

        name = 'test'
        fname = cronbook.g_file_path_root + name + cronbook.g_file_extension
        
        self.assertEqual( fname, cronbook.ds_filename(name) )

    #def test_ds_query(self):

    def test_ds_rename(self):

        t = open(cronbook.g_file_path_root + 'unittest_from', 'w')
        fname_to = 'unittest_to'
        cronbook.ds_rename(t.name, fname_to)
        
        self.assertTrue( os.path.isfile(fname_to) )

        t.close()
        os.remove(fname_to)
 
    def test_ds_row_write(self):

        t = tempfile.NamedTemporaryFile()

        schema = [cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp, 'key_1', 'key_2']
        values = ['0', cronbook.util_timestamp_format(0), 'value_1', 'value_2']
        file_representation = 'unixtime|timestamp|key_1|key_2\n0|' + cronbook.util_timestamp_format(0) + '|value_1|value_2\n'

        cronbook.ds_create(t, schema)
        cronbook.ds_row_write(t, values)

        t.seek(0)
        content = t.read()

        self.assertEqual(file_representation, content)

        t.close()

        with self.assertRaises(cronbook.DiskError):
            cronbook.ds_row_write(t, values)

    def test_ds_schema_modify(self):

        t = tempfile.NamedTemporaryFile()

        schema = [cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp, 'key_1', 'key_2']
        values = ['0', cronbook.util_timestamp_format(0), 'value_1', 'value_2']
        new_keys = ['key_3', 'key_4']
        file_representation = 'unixtime|timestamp|key_1|key_2|key_3|key_4\n0|' + cronbook.util_timestamp_format(0) + '|value_1|value_2||\n'

        cronbook.ds_create(t, schema)
        cronbook.ds_row_write(t, values)
        cronbook.ds_schema_modify(t, new_keys)

        t.seek(0)
        content = t.read()

        self.assertEqual(file_representation, content)

        t.close()

        file_exists = os.path.isfile(cronbook.g_file_temporary)
        self.assertEqual(file_exists, False)

        with self.assertRaises(cronbook.DiskError):
            cronbook.ds_schema_modify(t, new_keys)

    def test_ds_schema_read(self):

        t = tempfile.NamedTemporaryFile()

        schema = [cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp, 'key_1', 'key_2']

        cronbook.ds_create(t, schema)

        content = cronbook.ds_schema_read(t)

        self.assertEqual(schema, content)

        t.close()

        with self.assertRaises(cronbook.DiskError):
            content = cronbook.ds_schema_read(t)

    def test_ds_write(self):

        t = tempfile.NamedTemporaryFile()

        schema = [cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp, 'key_1', 'key_2']
        keys = [cronbook.g_key_name_unixtime, cronbook.g_key_name_timestamp, 'key_1', 'key_2']
        values = [['0', cronbook.util_timestamp_format(0), 'value_1', 'value_2']]
        file_representation = 'unixtime|timestamp|key_1|key_2\n0|' + cronbook.util_timestamp_format(0) + '|value_1|value_2\n'

        cronbook.ds_create(t, schema)
        cronbook.ds_write(t, keys, values)

        t.seek(0)
        content = t.read()

        self.assertEqual(file_representation, content)

        t.close()

        with self.assertRaises(cronbook.DiskError):
            cronbook.ds_write(t, keys, values)

if __name__ == '__main__':
    unittest.main()
