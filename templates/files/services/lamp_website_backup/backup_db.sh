#!/usr/bin/env bash
SSH_USER="{{ '{{ ssh_user }}' }}"
SSH_HOST="{{ '{{ backup_host }}' }}"
DB_USER="{{ '{{ db_user }}' }}"
DB_PASSWORD="{{ '{{ db_password }}' }}"
DB_NAME="{{ '{{ db_name }}' }}"
DUMP_DIR="{{ '{{ dump_dir }}' }}"
DUMP_SUFFIX="{{ '{{ dump_suffix }}' }}"
ssh -l ${SSH_USER} -i ~/.ssh/id_rsa_backup ${SSH_HOST} "mkdir -p ${DUMP_DIR}"
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME | gzip -3 -c > "/tmp/${DB_NAME}${DUMP_SUFFIX}.sql.gz"
scp -i /root/.ssh/id_rsa_backup "/tmp/${DB_NAME}${DUMP_SUFFIX}.sql.gz" "${SSH_USER}@${SSH_HOST}:/${DUMP_DIR}/${DB_NAME}${DUMP_SUFFIX}.sql.gz"
rm "/tmp/${DB_NAME}${DUMP_SUFFIX}.sql.gz"
# TODO: satache ansible creer /var/backups/services cree et appartient a user backup
