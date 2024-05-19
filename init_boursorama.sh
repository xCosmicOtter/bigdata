#!/bin/bash

download_and_extract() {
    url=$1
    target_dir=$2

    mkdir -p "$target_dir"
    echo "=== Downloading bourse.tar file at: $url"
    wget --progress=bar "$url" -O "$target_dir/archive.tar"

    if [ $? -ne 0 ]; then
        echo "Failed to download file from $url."
        exit 1
    fi

    echo "=== Extracting data from .tar"
    tar -xf "$target_dir/archive.tar" -C "$target_dir"

    # Remove the tar file after extraction
    rm -v "$target_dir/archive.tar"
}

# Usage
if [ $# -ne 2 ]; then
    echo "Usage: $0 <URL_NBR_TAR_ARCHIVE> <TARGET_DIRECTORY>"
    exit 1
fi

download_and_extract "$1" "$2"
