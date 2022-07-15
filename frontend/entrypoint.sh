#!/bin/sh

VUE_APP_API_CHUNK_SIZE_DEFAULT=5
ROOT_DIR=/usr/share/nginx/html

if [[ -z "${VUE_APP_API_CHUNK_SIZE}" ]]; then
    VUE_APP_API_CHUNK_SIZE="${VUE_APP_API_CHUNK_SIZE_DEFAULT}"
fi

echo "Replacing VUE_APP_API_CHUNK_SIZE constant in JS with ${VUE_APP_API_CHUNK_SIZE}"
for file in $ROOT_DIR/static/js/*.js* $ROOT_DIR/index.html;
do
    sed -i 's|VUE_APP_API_CHUNK_SIZE|'${VUE_APP_API_CHUNK_SIZE}'|g' $file
done

nginx -g 'daemon off;'
