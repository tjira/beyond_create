source ./download_mod.sh

generate_server() {
    local modpack_name=$1
    local neoforge_version=$2
    local memory=$3
    shift 3
    local mod_ids=("$@")

    download_installer "$neoforge_version"
    run_installer "$neoforge_version"
    accept_eula
    set_memory "$memory"
    generate_server_properties "$modpack_name"
    make_headless_linux
    make_headless_windows
    move_server_files
    clean_server_directory "$neoforge_version"

    for mod_id in "${mod_ids[@]}"; do
        download_mod "$mod_id" "server/mods"
    done
}

accept_eula() {
    echo "eula=true" > eula.txt
}

clean_server_directory() {
    local version=$1

    rm neoforge-$version-installer.jar*
}

download_installer() {
    local version=$1

    wget https://maven.neoforged.net/releases/net/neoforged/neoforge/$version/neoforge-$version-installer.jar
}

generate_server_properties() {
    local modpack_name=$1

    echo "motd=$modpack_name NeoForge Server" > server.properties
}

make_headless_linux() {
    sed -i '/^#/d' run.sh && sed -i '1s/$/ nogui/' run.sh
}

make_headless_windows() {
    sed -i '/^REM/d' run.bat && sed -i '2s/$/ nogui/' run.bat
}

move_server_files() {
    mkdir -p server && mv eula.txt run.bat run.sh server.properties user_jvm_args.txt libraries server
}

run_installer() {
    local version=$1

    java -jar neoforge-$version-installer.jar --installServer
}

set_memory() {
    local memory=$1

    echo "-Xmx$memory" > user_jvm_args.txt
}
