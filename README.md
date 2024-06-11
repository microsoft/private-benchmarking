# Private Benchmarking of Machine Learning Models

## Project Status
**Warning: This is an academic proof-of-concept prototype and has not received careful code review. This implementation is NOT ready for production use.

points
- [x] Need to change the null and blank default values to false in the models of file uploads (file:models.py)
- [x] ssl certificate security for the website (file:settings.py)
- [x] implement Trust level 1,2,3,4 and 5(done)
- [x] Testing
- [x] Documentation
- [x] CI/CD workflows for github actions
## Description

# Project Description

This project aims to create a platform that enables users to perform private benchmarking of machine learning models. The platform facilitates the evaluation of models based on different trust levels between the model owners and the dataset owners.

## Installation
for complete build and EzPC LLM support
```
./setup.sh
Enter the Server IP address: <your_server_IP>
```
only the platform
```
pip install -r requirements.txt
cd eval_website/eval_website
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Usage

To use the project after installation visit.

http://127.0.0.1:8000 or http://your_server_IP:8000

### Sample User Credentials
- Model Owner
    - username: ModelOwner
    - password: helloFriend
- Dataset Owner
    - username: DatasetOwner
    - password: helloFriend

certain ports are pre-assigned as follows:
- 8000: for the main website
- 8001: for the EzPC LLM secure communication with Trusted third party server
- 7000: for the Trusted execution environment to communicate with the website 
- 9000: for communication of Dataset owner with the website for receiving key files for EzPC
- 9001: for communication of Model owner with the website for receiving key files for EzPC

- ### TTP SERVER
- Environment Variable ENCRYPTION_KEY is required to be set for the TTP server to run (32 bytes/256 bits) key.
 ```
 export ENCRYPTION_KEY="32 bytes key"
 #generate a 32 bytes key using the following command
 python -c 'import os; print(os.urandom(32))'
 ```



## Contributing
If you would like to contribute to this project, please follow the guidelines outlined in the [contributing.md](CONTRIBUTING.md) file.

## License
This project is licensed under the [MIT] license. Please see the [LICENSE](LICENSE.txt) file for more information.
