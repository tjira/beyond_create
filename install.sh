MODPACK_NAME="Beyond Create"
MODPACK_VERSION="0.0.1"
NEOFORGE_VERSION="21.1.217"

MOD_VERSION_IDS=(
    ZdLtebKH
    8nuqyxbw
)

# DOWNLOAD NEOFORGE INSTALLER
wget https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEOFORGE_VERSION/neoforge-$NEOFORGE_VERSION-installer.jar

# RUN NEOFORGE INSTALLER
java -jar neoforge-$NEOFORGE_VERSION-installer.jar --installServer

# CLEAN UP INSTALLER
rm neoforge-$NEOFORGE_VERSION-installer.jar*

# SET JVM ARGS
echo "-Xmx4G" > user_jvm_args.txt

# ACCEPT EULA
echo "eula=true" > eula.txt

# DEFAULT SERVER PROPERTIES
echo "motd=$MODPACK_NAME NeoForge Server" > server.properties

# CLEAN UP RUN SCRIPTS
sed -i '/^REM/d' run.bat && sed -i '/^#/d' run.sh

# MAKE THE RUN SCRIPTS HEADLESS
sed -i '1s/$/ nogui/' run.sh && sed -i '2s/$/ nogui/' run.bat

# MAKE MODRINTH DIRECTORY TREE
mkdir -p modrinth/overrides

# CREATE THE MODRINTH MANIFEST
echo '{
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": "'$MODPACK_VERSION'",
    "name": "Beyond Create",
    "dependencies": {
        "minecraft": "1.21.1",
        "neoforge": "'$NEOFORGE_VERSION'"
    },
    "files": []
}' > modrinth/modrinth.index.json

# ADD THE MODS TO MANIFEST
for MOD_VERSION_ID in "${MOD_VERSION_IDS[@]}"; do

    # GET MODRINTH API RESPONSE
    API_RESPONSE=$(curl -Ls "api.modrinth.com/v2/version/$MOD_VERSION_ID")

    # EXTRACT THE FILENAME
    FILENAME=$(echo "$API_RESPONSE" | jq -r '.files[0].filename')

    # EXTRACT THE URL TO THE MOD FILE
    URL=$(echo "$API_RESPONSE" | jq -r '.files[0].url')

    # EXTRACT THE SHA1 HASH
    SHA1=$(echo "$API_RESPONSE" | jq -r '.files[0].hashes.sha1')

    # EXTRACT THE SHA512 HASH
    SHA512=$(echo "$API_RESPONSE" | jq -r '.files[0].hashes.sha512')

    # EXTRACT THE FILE SIZE
    SIZE=$(echo "$API_RESPONSE" | jq -r '.files[0].size')

    # APPEND TO FILES ARRAY
    jq '.files += [{
        "path" : "mods/'$FILENAME'",
        "hashes" : {
            "sha1" : "'$SHA1'",
            "sha512" : "'$SHA512'"
        },
        "env" : {
            "client" : "required",
            "server" : "required"
        },
        "downloads" : [
            "'$URL'"
        ],
        "fileSize" : '$SIZE'
    }]' modrinth/modrinth.index.json > temp.json && mv temp.json modrinth/modrinth.index.json

    # DOWNLOAD THE MOD FILE INTO THE MODS DIRECTORY
    wget -P server/mods "$URL"
done

# ZIP THE MODRINTH PACKAGE
cd modrinth && zip modrinth.zip modrinth.index.json overrides && cd ..

# CREATE THE MODPACKS DIRECTORY
mkdir -p modpacks

# RENAME THE MODRINTH PACKAGE
mv modrinth/modrinth.zip modpacks/$(echo "$MODPACK_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')_${MODPACK_VERSION}_client.mrpack

# REMOVE THE MODRINTH DIRECTORY
rm -r modrinth

# CREATE THE SERVER DIRECTORY
mkdir -p server

# MOVE THE SERVER FILES TO THE SERVER DIRECTORY
mv eula.txt run.bat run.sh server.properties user_jvm_args.txt libraries server
