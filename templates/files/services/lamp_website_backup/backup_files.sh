#!/usr/bin/env bash
SSH_USER="{{ '{{ ssh_user }}' }}"
SSH_HOST="{{ '{{ backup_host }}' }}"
SOURCE_DIR="{{ '{{ source_dir }}' }}"
TARGET_DIR="{{ '{{ target_dir }}' }}"
ssh -l ${SSH_USER} -i ~/.ssh/id_rsa_backup ${SSH_HOST} "mkdir -p ${TARGET_DIR}"
rsync -e 'ssh -i /root/.ssh/id_rsa_backup' -avz --delete-after ${SOURCE_DIR} ${SSH_USER}@${SSH_HOST}:${TARGET_DIR}
ssh -l ${SSH_USER} -i ~/.ssh/id_rsa_backup ${SSH_HOST} "touch ${TARGET_DIR}/last.touch"
