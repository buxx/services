#!/usr/bin/env bash
SSH_USER="{{ '{{ ssh_user }}' }}"
SSH_HOST="{{ '{{ ssh_host }}' }}"
DB_USER="{{ '{{ db_user }}' }}"
DB_PASSWORD="{{ '{{ db_password }}' }}"
DB_NAME="{{ '{{ db_name }}' }}"
DUMP_DIR="{{ '{{ dump_dir }}' }}"
DUMP_SUFFIX="{{ '{{ dump_suffix }}' }}"
mkdir -p ${DUMP_DIR}
ssh -l ${SSH_USER} ${SSH_HOST} "mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME | gzip -3 -c" > "${DUMP_DIR}/${DB_NAME}${DUMP_SUFFIX}.sql.gz"
# TODO: satache ansible créer /var/backups/services créé et appartient à user backup