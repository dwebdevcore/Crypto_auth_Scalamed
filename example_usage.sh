#!/usr/bin/env bash

domain="localhost:8000"

function generate_random_username() {
    alphabet='abcdefghijklmnopqrstuvwxyz'
    python -c "import random; print(''.join(random.choices('$alphabet', k=10)))"
}

username=$(generate_random_username)

# /auth/register
payload='{"email": "'"${username}"'@mail.com", "password": "Tr0ub4dor&3"}'
echo "${domain}/auth/register <= ${payload}"

result=$(curl\
    --silent\
    --request PUT\
    --data "${payload}"\
    "${domain}/auth/register")
echo "${domain}/auth/register => $result"


# /auth/login
echo "${domain}/auth/login <= ${payload}"

result=$(curl\
    --silent\
    --request POST\
    --data "${payload}"\
    "${domain}/auth/login")
echo "${domain}/auth/login => $result"
