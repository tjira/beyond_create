download_mod() {
    local id="$1"
    local dir="$2"

    local api_response=$(get_mod_api_response "$id")
    local url=$(get_mod_url "$api_response")

    wget -P "$dir" "$url"
}

get_mod_api_response() {
    local id="$1"

    curl -Ls "api.modrinth.com/v2/version/$id"
}

get_mod_filename() {
    local api_response="$1"

    echo "$api_response" | jq -r '.files[0].filename'
}

get_mod_sha1() {
    local api_response="$1"

    echo "$api_response" | jq -r '.files[0].hashes.sha1'
}

get_mod_sha512() {
    local api_response="$1"

    echo "$api_response" | jq -r '.files[0].hashes.sha512'
}

get_mod_size() {
    local api_response="$1"

    echo "$api_response" | jq -r '.files[0].size'
}

get_mod_url() {
    local api_response="$1"

    echo "$api_response" | jq -r '.files[0].url'
}
