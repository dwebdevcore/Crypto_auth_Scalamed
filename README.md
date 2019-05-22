# ScalaMed Auth

Authentication Service for the ScalaMed Project.

## Installation and Running

There are two ways to run/install this code, with or without docker. First, get
the repo:

```bash
$ git clone git@bitbucket.org:GyrixSigma/auth.git scalamed-auth
$ cd scalamed-auth
```

### Without Docker

```bash
# Install virtualenv and python3.X -- This is platform dependent.
$ ...

# Set up virtualenv with python3, and activate
$ virtualenv --python=python3 venv
$ source venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt

# Enter project
$ cd scalamed

# Migrate database and run
$ ./manage makemigrations
$ ./manage migrate
$ ./manage runserver

# Test the server
$ curl -v localhost:8000/auth/users
```

### With Docker

If you install [docker](https://www.docker.com/community-edition#/download), and
[docker-compose](https://docs.docker.com/compose/install/). Docker Compose can
be installed via Python's pip, if you prefer.

```bash
$ pip install docker-compose
```

After setting up docker and docker-compose you should be able to build and run
the app:

```bash
$ cd scalamed-auth
$ sudo docker-compose up --build -d
```

To bring it down (i.e. shutdown the app)

```bash
$ cd scalamed-auth
$ sudo docker-compose down
```

## API

This is the current state of the API.

| End Point                | Request Type | Parameters                               | Return                                    | Description                                        |
|:-------------------------|:------------:|:-----------------------------------------|:------------------------------------------|:---------------------------------------------------|
| /auth/login              |    `POST`    | ``{ email, password }``                  | ``{ token_level0, token_level1, uuid }``  | Login request - returns tokens                     |
| /auth/loginuuid          |    `POST`    | ``{ uuid }``                             | ``{ token_level0, token_level1}``         | Login request - returns tokens                     |
| /auth/register           |    `PUT`     | ``{ email, password }``                  | ``{ email }``                             | Registration for a user to Auth service            |
| /auth/forgotpw           |    `POST`    | ``{ email } ``                           | ``{ token }``                             | Forgot password                                    |
| /auth/resetpw            |    `POST`    | ``{ email, token } ``                    | ``{ success }``                           | Reset password                                     |
| /auth/check              |    `POST`    | ``{ uuid, token_level0, token_level1 }`` | ``{ success, token_level1 }``             | Check if token is valid                            |
| /auth/check/prescription |    `POST`    | ``{ uuid, token_level0, token_level1 }`` | ``{ success, token_level1 }``             | Checks if the UUID is valid to sign a prescription |
| /auth/check/fulfil       |    `POST`    | ``{ uuid, token_level0, token_level1 }`` | ``{ success, token_level1 }``             | Checks if the UUID is valid to fulfil              |
| /auth/getsecret          |    `POST`    | ``{ uuid, token_level0, token_level1 }`` | ``{ token_level1, secret }``              | Get the secret for the row encryption              |

