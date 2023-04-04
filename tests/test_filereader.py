from unittest import TestCase, main

from handlers_files.open_files import FileReader

from tests.files.filereader.input_data import header_megafon, megafon_number_fields, megafon_number_fields_

class TestFileReader(TestCase):

    def test_get_numbers_fields_magafon_meg(self):
        self.operator = 'Мегафон'
        self.assertEqual(FileReader.get_numbers_fields(self, header_megafon), megafon_number_fields)
    
    def test_get_numbers_fields_magafon_mts(self):
        self.operator = 'Мегафон'
        self.assertEqual(FileReader.get_numbers_fields(self, header_megafon), megafon_number_fields_)


if __name__ == '__main__':
    main()