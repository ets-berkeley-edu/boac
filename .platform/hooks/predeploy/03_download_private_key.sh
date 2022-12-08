#!/bin/bash
PYTHONPATH='' aws s3 cp s3://boac-deploy-configs/shared/certificate/boa-self-signed.key /tmp/boac_openssl_private.key
sudo mv /tmp/boac_openssl_private.key /etc/ssl/certs/boac_openssl_private.key
sudo chmod 400 /etc/ssl/certs/boac_openssl_private.key
sudo chown root:root /etc/ssl/certs/boac_openssl_private.key
