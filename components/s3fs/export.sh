#!/bin/sh
set -xe

ARG="$@"
EXPORT_TO="${EXPORT_TO:-$ARG}"

mkdir -p "${EXPORT_TO}"
mkdir -p "/opt/bin"

VENDOR="agilestacks"
DRIVER="goofysflex"

# driver_dir="$EXPORT_TO/$VENDOR${VENDOR:+"~"}${DRIVER}"
driver_dir="$EXPORT_TO/$DRIVER"
mkdir -p "${driver_dir}"

rm -rf "${driver_dir}/goofysflex"
# rm -rf "${driver_dir}/goofysflex.log"

yes | cp -fn "/usr/bin/goofys" "${driver_dir}"
yes | cp -f "/usr/bin/goofysflex" "${driver_dir}"
yes | cp -fn "/usr/bin/fusermount" "${driver_dir}"
yes | cp -fn "/usr/bin/tini" "${driver_dir}"

# yes | cp -f "/usr/bin/dummy" "${EXPORT_TO}/dummy"
