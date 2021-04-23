# Study Project for system architecture 
#### Service responsible for uploading and downloading data.
![Build Status](https://img.shields.io/github/workflow/status/unbrokenguy/sys-arch-server/lint?label=linters)
* [Installation](#installation)
* [Setup](#setup)
* [Usage](#usage)
* [Related repositories](#related-repositories)
## Installation

#### Install poetry
```shell
pip install poetry
```

#### Install the project dependencies
```shell
poetry install 
```

## Setup

#### Make sure you have installed and started these servers in this order 
1. [Configuration Server](https://github.com/unbrokenguy/sys-arch-conf-app)
2. [Authorization Server](https://github.com/unbrokenguy/sys-arch-auth-app)

### Start current server
#### Spawn a shell within the virtual environment
```shell
poetry shell
```
#### Add environments
* SECRET_KEY: Your secret key for django application.
* CONF_APP_IP: [Configuration Server](https://github.com/unbrokenguy/sys-arch-conf-app) url
* AUTH_APP_IP: [Authorization Server](https://github.com/unbrokenguy/sys-arch-auth-app) url

#### Start server
```shell
cd src && python manage.py runserver
```
Server will be available at this url  `http://localhost:8000/` or `http://127.0.0.1:8000/`
## Usage
#### Only authorized users can make requests.
* POST `/auth/sign_in/` - Redirect to [Authorization Server](https://github.com/unbrokenguy/sys-arch-auth-app).
* POST `/auth/sign_up/` - Redirect to [Authorization Server](https://github.com/unbrokenguy/sys-arch-auth-app).
* POST `/data/` - Upload data (strings or files).
* GET `/category/` - List of categories.
* GET `/data/{pk}/` - Download data.
* GET `/category/{pk}/` - Retrieve category.
## Related repositories
1. [Configuration Server](https://github.com/unbrokenguy/sys-arch-conf-app)
2. [Authorization Server](https://github.com/unbrokenguy/sys-arch-auth-app)
3. [Command line client](https://github.com/unbrokenguy/sys-arch-client)
4. [Front end](https://github.com/niyazm524/arch_client_web)