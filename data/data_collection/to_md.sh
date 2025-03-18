#!/bin/bash

if [ -z "$1" ] || [ -z "$2"]; then
    echo "Usage: $0 <directory>"
    exit 1
fi


INPUT_DIR="$1"
OUTPUT_DIR="$2"


mkdir -p "$OUTPUT_DIR"

convert_file() {
    local input_file="$1"
    local output_file="$2"

    echo "Converting $input_file to $output_file"
    mkdir -p "$(dirname "$output_file")"
    markitdown "$input_file" > "$output_file"
}


find "$INPUT_DIR" -type d | while read -r folder; do
    relative_folder="${folder#$INPUT_DIR/}"
    output_folder="$OUTPUT_DIR/$relative_folder"
    mkdir -p "$output_folder"


    find "$folder" -maxdepth 1 -type f -name '*.docx' | while read -r docx; do
        base_name=$(basename "${docx%.*}")
        output_file="$output_folder/$base_name.md"
        if [[ ! -f "$output_file" ]]; then
            convert_file "$docx" "$output_file"
        fi
    done


    find "$folder" -maxdepth 1 -type f -name '*.pdf' | while read -r pdf; do
        base_name=$(basename "${pdf%.*}")
        output_file="$output_folder/$base_name.md"
        if [[ ! -f "$output_file" ]]; then
            convert_file "$pdf" "$output_file"
        fi
    done
done

echo "Conversion complete."
