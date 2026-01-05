generate_modpack() {
    local modpack_name=$1
    local minecraft_version=$2
    local neoforge_version=$3
    local modpack_version=$4
    shift 4
    local mod_ids=("$@")

    generate_base_manifest "$modpack_name" "$minecraft_version" "$neoforge_version" "$modpack_version"

    for mod_id in "${mod_ids[@]}"; do
        append_mod_info_to_manifest "$mod_id"
    done

    zip_generated_modpack "$modpack_name" "$minecraft_version" "$modpack_version"
    clean_modpack_directory
}

append_mod_info_to_manifest() {
    local mod_id=$1

    api_response=$(get_mod_api_response "$mod_id")
    filename=$(get_mod_filename "$api_response")
    sha1=$(get_mod_sha1 "$api_response")
    sha512=$(get_mod_sha512 "$api_response")
    size=$(get_mod_size "$api_response")
    url=$(get_mod_url "$api_response")

    jq '.files += [{
        "path" : "mods/'$filename'",
        "hashes" : {
            "sha1" : "'$sha1'",
            "sha512" : "'$sha512'"
        },
        "env" : {
            "client" : "required",
            "server" : "required"
        },
        "downloads" : [
            "'$url'"
        ],
        "fileSize" : '$size'
    }]' modpack/modrinth.index.json > temp.json && mv temp.json modpack/modrinth.index.json
}

clean_modpack_directory() {
    rm -rf modpack/modrinth.index.json modpack/overrides
}

generate_base_manifest() {
    local modpack_name=$1
    local minecraft_version=$2
    local neoforge_version=$3
    local modpack_version=$4

    mkdir -p modpack/overrides

    echo '{
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": "'$modpack_version'",
        "name": "'$modpack_version'",
        "dependencies": {
            "minecraft": "'$minecraft_version'",
            "neoforge": "'$neoforge_version'"
        },
        "files": []
    }' > modpack/modrinth.index.json
}

get_modpack_filename_client() {
    local modpack_name=$1
    local minecraft_version=$2
    local modpack_version=$3


    echo $(echo "$modpack_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')_MC${minecraft_version}_v${modpack_version}_client.mrpack
}

zip_generated_modpack() {
    local modpack_name=$1
    local minecraft_version=$2
    local modpack_version=$3

    filename=$(get_modpack_filename_client "$modpack_name" "$minecraft_version" "$modpack_version")

    cd modpack && zip temp.zip modrinth.index.json overrides && mv temp.zip $filename && cd ..
}
