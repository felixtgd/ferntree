#!/bin/bash

source .env

project_name="ferntree"
s3_alias="${project_name}-s3"
bucket_name="${project_name}-state"
region="fsn1"
hetzner_endpoint="https://fsn1.your-objectstorage.com"

# Install minio client
if [ ! -x "./mc" ]; then
    echo "MinIO client (mc) not found. Installing..."
    wget https://dl.min.io/client/mc/release/linux-amd64/mc
    chmod +x mc
else
    echo "MinIO client (mc) is already installed."
fi

# configure minio client with the S3 credentials from the .env file
if ! ./mc alias ls | grep -q "${s3_alias}"; then
    ./mc alias set ${s3_alias} \
        ${hetzner_endpoint} \
        $S3_ACCESS_KEY $S3_SECRET_KEY \
        --api "s3v4" \
        --path "off"
else
    echo "MinIO client alias '${s3_alias}' is already configured."
fi

# create bucket
if ! ./mc ls ${s3_alias} | grep "${bucket_name}"; then
    ./mc mb ${s3_alias}/${bucket_name} --region ${region}
else
    echo "Bucket '${bucket_name}' already exists in the '${s3_alias}' alias."
fi
