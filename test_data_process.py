import pytest
import responses
from unittest.mock import patch
from requests.exceptions import ConnectionError, HTTPError

from data_process import DataProcess


SOCCER_URL = 'http://codekata.com/data/04/football.dat'


@pytest.fixture
def soccer_data_obj():
    return DataProcess(
        SOCCER_URL,
        key_column_index=1,
        spread_columns_indexes=(6, 8),
        validation_func=lambda line: len(line) == 10
    )


class TestDataProcess:
    @responses.activate
    def test_get_data_unsuccessful_request(self, soccer_data_obj):
        responses.add(responses.GET, SOCCER_URL, status=404)
        with pytest.raises(HTTPError):
            soccer_data_obj._get_data()

    @responses.activate
    def test_get_data_connection_error(self, soccer_data_obj):
        responses.add(responses.GET, SOCCER_URL, body=ConnectionError(''))
        with pytest.raises(ConnectionError):
            soccer_data_obj._get_data()

    @responses.activate
    def test_get_data_200(self, soccer_data_obj):
        responses.add(responses.GET, SOCCER_URL, status=200,
                      body='Some response')
        data = soccer_data_obj._get_data()
        assert data == 'Some response'

    def test_get_valid_data(self, soccer_data_obj):
        data = (
            '       Team            P     W    L   D    F      A     Pts\n'
            '    1. Arsenal         38    26   9   3    79  -  36    87\n'
            '     -----------\n'
            '   18. Ipswich         38     9   9  20    41  -  64    36\n'
            '   19. Derby           38     8   6  24    33  -  \n'
        )
        expected = [
            ['1.', 'Arsenal', '38', '26', '9', '3', '79', '-', '36', '87'],
            ['18.', 'Ipswich', '38', '9', '9', '20', '41', '-', '64', '36'],
        ]
        split_data = soccer_data_obj._get_valid_data(data)
        assert list(split_data) == expected

    @patch('data_process.DataProcess._get_spread')
    def test_get_min_spread(self, mock_spread, soccer_data_obj):
        data = iter([
            ['1.', 'Arsenal', '38', '26', '9', '3', '79', '-', '36', '87'],
            ['18.', 'Ipswich', '38', '9', '9', '20', '41', '-', '64', '36'],
            ['17.', 'Sunder', '38', '10', '10', '18', '29', '-', '52', '40'],
        ])
        mock_spread.side_effect = [43, 23, 23]
        result = soccer_data_obj._get_key_of_min_spread(data)
        assert result == 'Ipswich'

    @pytest.mark.parametrize('line_list,expected_spread', [
        (['1.', 'Widzew', '38', '26', '9', '3', '79', '-', '36', '87'], 43),
        (['1.', 'Lech', '38', '26', '9', '3', '79*', '-', '*36', '87'], 43),
        (['14.', 'Lech', '38', '10', '14', '14', '38', '-', '49', '44'], 11),
    ])
    def test_get_spread(self, line_list, expected_spread, soccer_data_obj):
        spread = soccer_data_obj._get_spread(line_list)
        assert spread == expected_spread

    @patch('logging.Logger.error')
    @patch('data_process.DataProcess._get_data')
    def test_get_min_spread_from_file_error_on_fetch(
            self, mock_get_data, mock_log, soccer_data_obj):
        mock_get_data.side_effect = HTTPError()
        soccer_data_obj.get_min_spread_from_file()
        mock_get_data.assert_called_once()
        mock_log.assert_called_once_with(
            'Error on fetching the data - please check '
            'Internet connection or URL.', exc_info=True
        )

    @patch('logging.Logger.error')
    @patch('data_process.DataProcess._get_data')
    @pytest.mark.parametrize('obj_args', [
        (SOCCER_URL, 1, (6, 8), 'test'),
        (SOCCER_URL, 1, (60, 80), 'lambda x: x'),
    ])
    def test_get_min_spread_from_file_error_on_parse(
            self, mock_get_data, mock_log, obj_args):
        data_obj = DataProcess(*obj_args)
        mock_get_data.return_value = (
            '       Team            P     W    L   D    F      A     Pts\n'
            '    1. Arsenal         38    26   9   3    79  -  36    87\n'
        )
        data_obj.get_min_spread_from_file()
        mock_get_data.assert_called_once()
        mock_log.assert_called_once_with(
            'Error on parsing the data - please check '
            'properties of DataProcess creation.', exc_info=True
        )

    @patch('data_process.DataProcess._get_data')
    @patch('data_process.DataProcess._get_valid_data')
    @patch('data_process.DataProcess._get_key_of_min_spread')
    def test_get_min_spread_from_file_check_calls(
            self, mock_min_spread, mock_valid_data, mock_get_data,
            soccer_data_obj
    ):
        mock_get_data.return_value = 'data'
        mock_valid_data.return_value = ['valid_data']
        soccer_data_obj.get_min_spread_from_file()
        mock_valid_data.assert_called_once_with('data')
        mock_min_spread.assert_called_once_with(['valid_data'])

    @pytest.mark.parametrize('args,expected_error_msg', [
        (('', 1, (1, 2), lambda x: x),
         'URL must be provided'),
        (('test_url', '1', (1, 2), lambda x: x),
         'key_column_index must be an integer'),
        (('test_url', 1, (1, 2, 3), lambda x: x),
         'spread_columns_indexes must be tuple of 2 integers'),
        (('test_url', 1, (1,), lambda x: x),
         'spread_columns_indexes must be tuple of 2 integers'),
        (('test_url', 1, ('1', '2'), lambda x: x),
         'spread_columns_indexes must be tuple of 2 integers'),
        (('test_url', 1, [1, 2], lambda x: x),
         'spread_columns_indexes must be tuple of 2 integers'),
    ])
    def test_invalid_data_process_url(self, args, expected_error_msg):
        with pytest.raises(AssertionError) as e:
            DataProcess(*args)
        assert e.value.args == (expected_error_msg,)
