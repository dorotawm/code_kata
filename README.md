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
