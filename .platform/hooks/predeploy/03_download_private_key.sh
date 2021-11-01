#!/bin/bash
PYTHONPATH='' aws s3 cp s3://la-deploy-configs/shared/certificate/boac-self-signed-2020.key /tmp/boac_openssl_private.key
sudo mv /tmp/boac_openssl_private.key /etc/ssl/certs/boac_openssl_private.key
sudo chmod 400 /etc/ssl/certs/boac_openssl_private.key
sudo chown root:root /etc/ssl/certs/boac_openssl_private.key
