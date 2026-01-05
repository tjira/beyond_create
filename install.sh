NEOFORGE_VERSION="21.1.217"

MODS=(
    https://cdn.modrinth.com/data/sk9knFPE/versions/ZdLtebKH/rhino-2101.2.7-build.81.jar # https://modrinth.com/mod/rhino
    https://cdn.modrinth.com/data/umyGl7zF/versions/8nuqyxbw/kubejs-neoforge-2101.7.2-build.348.jar # https://modrinth.com/mod/kubejs
)

# DOWNLOAD NEOFORGE INSTALLER
wget https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEOFORGE_VERSION/neoforge-$NEOFORGE_VERSION-installer.jar

# RUN NEOFORGE INSTALLER
java -jar neoforge-$NEOFORGE_VERSION-installer.jar --installServer

# CLEAN UP INSTALLER
rm neoforge-$NEOFORGE_VERSION-installer.jar*

# SET JVM ARGS
echo "-Xmx4G" > user_jvm_args.txt

# CLEAN UP RUN SCRIPTS
sed -i '/^REM/d' run.bat && sed -i '/^#/d' run.sh

# MAKE THE RUN SCRIPTS HEADLESS
sed -i '1s/$/ nogui/' run.sh && sed -i '2s/$/ nogui/' run.bat

# ACCEPT EULA
echo "eula=true" > eula.txt

# DEFAULT SERVER PROPERTIES
echo "motd=Beyond Create NeoForge Server" > server.properties

# DOWNLOAD MODS
for MOD_URL in "${MODS[@]}"; do wget -P mods "$MOD_URL"; done
