import logging
from typing import Callable, Generator, List, Tuple

import requests

_LOGGER = logging.getLogger(__name__)


class DataProcess:
    def __init__(
            self, url: str, key_column_index: int,
            spread_columns_indexes: Tuple[int, int], validation_func: Callable
    ):
        assert url and isinstance(url, str), 'URL must be provided'
        assert isinstance(key_column_index, int),\
            'key_column_index must be an integer'
        assert (
            spread_columns_indexes
            and isinstance(spread_columns_indexes, Tuple)
            and len(spread_columns_indexes) == 2
            and isinstance(spread_columns_indexes[0], int)
            and isinstance(spread_columns_indexes[1], int)), \
            'spread_columns_indexes must be tuple of 2 integers'
        self.url = url
        self.key_index = key_column_index
        self.spread_indexes = spread_columns_indexes
        self.validation_func = validation_func

    def get_min_spread_from_file(self):
        try:
            data = self._get_data()
        except (requests.ConnectionError, requests.HTTPError):
            _LOGGER.error('Error on fetching the data - please check '
                          'Internet connection or URL.', exc_info=True)
            return None
        try:
            data = self._get_valid_data(data)
            min_spread = self._get_min_spread(data)
        except (IndexError, TypeError):
            _LOGGER.error(
                'Error on parsing the data - please check '
                'properties of DataProcess creation.', exc_info=True)
            return None
        return min_spread

    def _get_data(self) -> str:
        data = requests.get(self.url)
        data.raise_for_status()
        return data.text

    def _get_valid_data(self, data: str) -> Generator[List[str], None, None]:
        data_lines = data.splitlines()
        return (
            line.split()
            for line in data_lines[1:]
            if self.validation_func(line.split())
        )

    def _get_min_spread(self, data: Generator[List[str], None, None]) -> str:
        results = (
            (line[self.key_index], self._get_spread(line)) for line in data
        )
        # Assuming first minimum value is enough
        return min(results, key=lambda x: x[1])[0]

    def _get_spread(self, line: List) -> int:
        return abs(
            int(line[self.spread_indexes[0]].replace('*', ''))
            - int(line[self.spread_indexes[1]].replace('*', ''))
        )


if __name__ == "__main__":  # pragma: no cover
    soccer_process = DataProcess(
        'http://codekata.com/data/04/football.dat',
        key_column_index=1, spread_columns_indexes=(6, 8),
        validation_func=lambda line: len(line) == 10
    )
    print(soccer_process.get_min_spread_from_file())

    weather_process = DataProcess(
        'http://codekata.com/data/04/weather.dat',
        key_column_index=0, spread_columns_indexes=(1, 2),
        validation_func=lambda line: (
            line and len(line) > 3 and line[0].isdigit()
        )
    )
    print(weather_process.get_min_spread_from_file())
