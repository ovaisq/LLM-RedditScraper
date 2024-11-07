#!/bin/bash

# pg_dump backup in parallel, tar and encrypt the directory
# crontab:
#
#	0 * * * * /var/lib/postgresql/backup_encrypt_db.sh
#

# passphrase
export luks="<use strong passphrase here - 64 chars or more>"

create_directory() {
    local dir_path=$1

    # Check if the directory exists
    if [ -d "$dir_path" ]; then
        echo "Directory $dir_path already exists."
    else
        # Create the directory
        mkdir -p "$dir_path"
        echo "Directory $dir_path created successfully."
    fi
}


db_name="rollama"
backup_path="backups/dump_pg"
dir_name="${db_name}_"$(date '+%s')
dir_path="${backup_path}/${dir_name}"

create_directory "${dir_path}"

cd ~/${dir_path}

echo "Backing up pg_dump ${db_name}"
pg_dump -j 2 -F d -f "${PWD}" ${db_name} | split -b 1G --filter='gzip > "$db_name_"$FILE.gz'

echo "Changing directory"
cd ..
echo "${PWD}"

echo "Archiving Directory ${dir_name}"
tar cvf ${dir_name}.tar ${dir_name} >/dev/null 2>&1

echo "Encrypting Directory ${dir_name}"
scrypt enc --passphrase env:luks ${dir_name}.tar ${dir_name}.tar.enc

if [ $? -eq 0 ]
then
	rm -rf ${dir_name} && rm -f ${dir_name}.tar
	echo "Encrypted backup file ${dir_name}.tar.enc created"
	exit 0
else
	echo "encryption failed for ${dir_name}.tar in ${PWD}"
	exit -1
fi
