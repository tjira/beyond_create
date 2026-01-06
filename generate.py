#!/usr/bin/env python3

import argparse, contextlib, functools, json, logging, os, re, requests, shutil, subprocess, tempfile

MODPACK_NAME = "Beyond Create"
MINECRAFT_VERSION = "1.20.1"
LOADER_VERSION = "0.18.4"
INSTALLER_VERSION = "1.1.1"
MODPACK_VERSION = "0.1.0"

FABRIC_URL = f"https://meta.fabricmc.net/v2/versions/loader/{MINECRAFT_VERSION}/{LOADER_VERSION}/{INSTALLER_VERSION}/server/jar"

MOD_IDS = {
    "Xaero's Minimap" : "6MQBeVDz",
    "Xaero's World Map" : "qNqsa3I3",
    "AppleSkin" : "xcauwnEB",
    "Fabric API" : "UapVHwiP",
    "TerraBlender" : "J1S3aA8i",
    "Biomes O' Plenty" : "eZaag2ca",
    "GlitchCore" : "25HLOiOl",
    "Jade" : "drol2x1P",
    "EMI" : "VvPw7Vi5",
    "Lithium" : "iEcXOkz4",
    "Architectury API" : "WbL7MStR",
    "Trinkets" : "AHxQGtuC",
}

MOD_IDS_SERVER = {
    "Log Begone" : "IknbjT7v",
} | MOD_IDS

MOD_IDS_CLIENT = {
    "Sodium" : "OihdIimA",
    "Iris" : "s5eFLITc",
    "Mod Menu" : "lEkperf6",
    "BetterF3" : "7WkFnw9F",
    "Entity Culling" : "QFXoqZHC",
    "ImmediatelyFast" : "AIFWhP2u",
} | MOD_IDS

SHADERS = {
    "Complementary Shaders - Unbound" : "LXrX6oqm"
}

MODPACK_FILENAME = f"{MODPACK_NAME.lower().replace(' ', '_')}_MC{MINECRAFT_VERSION}_v{MODPACK_VERSION}_client.mrpack"

MODRINTH_INDEX = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": MODPACK_VERSION,
    "name": MODPACK_NAME,
    "dependencies": {
        "minecraft": MINECRAFT_VERSION,
        "fabric-loader": LOADER_VERSION
    },
    "files": []
}

CLIENT_OPTIONS = [
    f"fullscreen:true",
    f"guiScale:2",
    f"renderDistance:16",
    f"simulationDistance:16",
]

SERVER_PROPERTIES = [
    f"motd=Welcome to the {MODPACK_NAME} Fabric Server!",
    f"view-distance=16",
    f"simulation-distance=16",
    f"gamemode=creative",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# LOGGING DECORATORS ===================================================================================================================================================================================

def archiveFolderLog(f):
    w = lambda p, a: [logging.info(f"Archiving the \"{p}\" folder to \"{a}\" archive"), f(p, a)][1]; return w

def downloadFileLog(f):
    w = lambda u, d: [logging.info(f"Downloading the \"{u}\" file to \"{d}\""), f(u, d)][1]; return w

def executeCommandLog(f):
    w = lambda c: [logging.info(f"Executing the \"{c}\" command"), f(c)][1]; return w

def getModMetadataLog(f):
    w = lambda n, i: [logging.info(f"Fetching metadata for the \"{n}\" with ID \"{i}\""), f(n, i)][1]; return w

# DEFINED FUNCTIONS ====================================================================================================================================================================================

@archiveFolderLog
def archiveFolder(folder_path, archive_name):
    shutil.make_archive(archive_name, "zip", folder_path); shutil.move(f"{archive_name}.zip", archive_name)

@downloadFileLog
def downloadFile(url, dest):
    with open(dest, "wb") as file: file.write(requests.get(url).content)

def downloadMod(mod_metadata, dest_dir):
    os.path.exists(path := os.path.join(dest_dir, mod_metadata["files"][0]["filename"])) or downloadFile(mod_metadata["files"][0]["url"], path)

@executeCommandLog
def executeCommand(command):
    subprocess.run(command, capture_output=False, shell=True, stdout=subprocess.DEVNULL)

def filterLines(string, prefix):
    return "\n".join([line for line in string.split("\n") if not line.startswith(prefix)])

@getModMetadataLog
def getModMetadata(name, mod_id):
    return requests.get(f"https://api.modrinth.com/v2/version/{mod_id}").json()

def generateModEntry(mod_metadata):
    return {
        "path": f"mods/{mod_metadata['files'][0]['filename']}",
        "hashes": {
            "sha1": mod_metadata["files"][0]["hashes"]["sha1"],
            "sha512": mod_metadata["files"][0]["hashes"]["sha512"]
        },
        "env": {
            "client": "required",
            "server": "required"
        },
        "downloads": [
            mod_metadata["files"][0]["url"]
        ],
        "fileSize": mod_metadata["files"][0]["size"]
    }

def readFile(filename):
    with open(filename, "r") as file: return file.read()

def writeToFile(filename, content):
    with open(filename, "w") as file: file.write(content + "\n")

# MAIN EXECUTION =======================================================================================================================================================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__), description="Server and Client Generator for the {MODPACK_NAME} Modpack",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=128),
        add_help=False, allow_abbrev=False
    )

    parser.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS, help="This help message.")

    parser.add_argument("--client", action="store_true", help="Generate the client modpack.")
    parser.add_argument("--server", action="store_true", help="Generate the server files.")

    parser.add_argument("--memory", type=str, default="4G", help="Maximum memory allocation for the server.")

    args = parser.parse_args()

    def modpack(directory):
        os.makedirs(os.path.join(directory, "overrides", "shaderpacks"), exist_ok=True)

        for mod in MOD_IDS_CLIENT.items():
            MODRINTH_INDEX["files"].append(generateModEntry(getModMetadata(*mod)))

        for shader in SHADERS.items():
            downloadMod(getModMetadata(*shader), os.path.join(directory, "overrides", "shaderpacks"))

        writeToFile(os.path.join(directory, "modrinth.index.json"     ), json.dumps(MODRINTH_INDEX, indent=4))
        writeToFile(os.path.join(directory, "overrides", "options.txt"), "\n".join(CLIENT_OPTIONS)           )

        archiveFolder(directory, MODPACK_FILENAME)

    def mserver(directory):
        os.makedirs("server", exist_ok=True)

        downloadFile(FABRIC_URL, os.path.join("server", "server.jar"))

        writeToFile(os.path.join("server", "run.sh" ), f"java -Xmx{args.memory} -jar server.jar nogui")

        os.chmod(os.path.join("server", "run.sh"), 0o755)

        writeToFile(os.path.join("server", "eula.txt"         ), f"eula=true"                )
        writeToFile(os.path.join("server", "server.properties"), "\n".join(SERVER_PROPERTIES))

        os.makedirs(os.path.join("server", "mods"), exist_ok=True)

        for mod in (item for item in MOD_IDS_SERVER.items() if args.server):
            downloadMod(getModMetadata(*mod), os.path.join("server", "mods"))

        shutil.copytree("config", os.path.join("server", "config"), dirs_exist_ok=True)

    with tempfile.TemporaryDirectory() as temp: modpack(temp) if args.client else None
    with tempfile.TemporaryDirectory() as temp: mserver(temp) if args.server else None
