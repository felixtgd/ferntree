#!/bin/bash

# Find the path to the certifi certificate bundle
CERT_PATH=$(python -m certifi)

# Set the SSL_CERT_FILE environment variable to the path you copied
# echo "export SSL_CERT_FILE=$CERT_PATH" >> ~/.zshrc
echo "export SSL_CERT_FILE=$CERT_PATH" >> ~/.bash_profile

# Apply the changes
# source ~/.zshrc
# Apply the changes
source ~/.bash_profile
