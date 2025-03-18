#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

TARGET_DIR="$1"

find "$TARGET_DIR" -type f -name '*\(1\)*' -exec rm -v {} \;
find "$TARGET_DIR" -type f -name '*\(2\)*' -exec rm -v {} \;
find "$TARGET_DIR" -type f -name '*\(3\)*' -exec rm -v {} \;

echo "Deletion complete."
