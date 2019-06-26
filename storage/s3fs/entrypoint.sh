#!/bin/sh

set -e

S3_ACL="${S3_ACL:-private}"
# OPTS="${OPTS:-nosuid,nonempty,nodev,allow_other,default_acl=${S3_ACL},retries=5}"
OPTS="${OPTS:-use_path_request_style,nosuid,nonempty,nodev,allow_other,default_acl=${S3_ACL},retries=5}"
if ! test -z "$S3_ENDPOINT"; then
	OPTS="${OPTS} -o url=${S3_ENDPOINT}"
fi

export S3_BUCKET="${S3_BUCKET:-default}"

if test -z "${IAM_ROLE}"; then
	export AWSACCESSKEYID="${AWSACCESSKEYID:-$AWS_ACCESS_KEY_ID}"
	export AWSSECRETACCESSKEY="${AWSSECRETACCESSKEY:-$AWS_SECRET_ACCESS_KEY}"
else
	OPTS="${OPTS} -o iam_role=${IAM_ROLE}"
fi

(
	echo "Starting s3fs"
	set -x 
	s3fs "${S3_BUCKET}" "/data" -d -f -o ${OPTS} $@ &
	set +x
	echo "s3fs started"
)

# if test "${NFS_SERVER}" -eq "1"; then
# 	(
# 		echo "Starting nfs"
# 		set -x 
# 		nfs-entrypoint "/data"
# 		set +x
# 		echo "nfs started"
# 	)
# fi

sleep infinity
