#!/bin/bash
PYTHONPATH='' aws s3 cp s3://boac-deploy-configs/shared/security/CIS-OS-Security-Config-Benchmarks-1.0/sshd_config/sed_commands_default.v1 /tmp/sed_commands
sudo chown root:root /etc/ssh/sshd_config
sudo chmod og-rwx /etc/ssh/sshd_config
sudo cp -p /etc/ssh/sshd_config /etc/ssh/sshd_config.default
sudo cp -p /etc/ssh/sshd_config /etc/ssh/sshd_config.new
sudo test -f /tmp/sed_commands && sudo sed -i -f /tmp/sed_commands /etc/ssh/sshd_config.new
sudo /usr/sbin/sshd -t -f /etc/ssh/sshd_config.new && sudo mv /etc/ssh/sshd_config.new /etc/ssh/sshd_config
