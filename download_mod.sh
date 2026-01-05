download_mod() {
    local id="$1"
    local dir="$2"

    local url=$(get_mod_url "$id")

    wget -P "$dir" "$url"
}

get_mod_api_response() {
    local id="$1"

    curl -Ls "api.modrinth.com/v2/version/$id"
}

get_mod_filename() {
    local id="$1"

    local api_response=$(get_mod_api_response "$id")

    echo "$api_response" | jq -r '.files[0].filename'
}

get_mod_sha1() {
    local id="$1"

    local api_response=$(get_mod_api_response "$id")

    echo "$api_response" | jq -r '.files[0].hashes.sha1'
}

get_mod_sha512() {
    local id="$1"

    local api_response=$(get_mod_api_response "$id")

    echo "$api_response" | jq -r '.files[0].hashes.sha512'
}

get_mod_size() {
    local id="$1"

    local api_response=$(get_mod_api_response "$id")

    echo "$api_response" | jq -r '.files[0].size'
}

get_mod_url() {
    local id="$1"

    local api_response=$(get_mod_api_response "$id")

    echo "$api_response" | jq -r '.files[0].url'
}
