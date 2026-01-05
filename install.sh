source ./download_mod.sh
source ./generate_modpack.sh
source ./generate_server.sh
source ./modpack_variables.sh

generate_server "$MODPACK_NAME" "$NEOFORGE_VERSION" "$SERVER_MEMORY" "${MOD_IDS_SERVER[@]}"
generate_modpack "$MODPACK_NAME" "$MINECRAFT_VERSION" "$NEOFORGE_VERSION" "$MODPACK_VERSION" "${MOD_IDS_ALL[@]}"
