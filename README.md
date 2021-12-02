This is simple project that reads 2 files.

1. Weather Data

    File is downloaded from http://codekata.com/data/04/weather.dat - program outputs the day number (column one) with the smallest temperature spread (the maximum temperature is the second column, the minimum the third column).

2. Soccer League Table

    File is downloaded from http://codekata.com/data/04/football.dat - program outputs the name of the team with the smallest difference in ‘for’ and ‘against’ goals. The columns labeled ‘F’ and ‘A’ contain the total number of goals scored for and against each team in that season.


Environment is managed by pipenv

After installing pipenv activate the environment by

    pipenv shell
    
Install packages

	pipenv install
	
Run program
    
    python data_process.py
    
Run tests and code checks

    flake8
    pytest --cov-report term-missing --cov=data_process test_data_process.py
