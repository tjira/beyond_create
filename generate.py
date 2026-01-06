#!/usr/bin/env python3

import argparse, contextlib, functools, json, logging, os, re, requests, shutil, subprocess, tempfile

MODPACK_NAME = "Beyond Create"
MINECRAFT_VERSION = "1.21.1"
NEOFORGE_VERSION = "21.1.217"
MODPACK_VERSION = "0.1.0"
SERVER_MEMORY = "4G"

NEOFORGE_URL = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{NEOFORGE_VERSION}/neoforge-{NEOFORGE_VERSION}-installer.jar"

MOD_IDS_SERVER = {
    "Rhino": "ZdLtebKH",
    "KubeJS": "8nuqyxbw",
    "AppleSkin": "kztxpjAA",
}

MOD_IDS_CLIENT = {
    "Sodium": "Pb3OXVqC",
    "Xaero's World Map": "xUpTkg0V",
    "Xaero's Minimap": "puXrtfcK",
    "Iris": "t3ruzodq",
}

MODPACK_FILENAME = f"{MODPACK_NAME.lower().replace(' ', '_')}_MC{MINECRAFT_VERSION}_v{MODPACK_VERSION}_client.mrpack"

MODRINTH_INDEX = {
    "formatVersion": 1,
    "game": "minecraft",
    "versionId": MODPACK_VERSION,
    "name": MODPACK_NAME,
    "dependencies": {
        "minecraft": MINECRAFT_VERSION,
        "neoforge": NEOFORGE_VERSION
    },
    "files": []
}

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

    args = parser.parse_args()

    def modpack(directory):
        os.makedirs(os.path.join(directory, "overrides"), exist_ok=True)

        for mod in (MOD_IDS_SERVER | MOD_IDS_CLIENT).items():
            MODRINTH_INDEX["files"].append(generateModEntry(getModMetadata(*mod)))

        open(os.path.join(directory, "modrinth.index.json"), "w").write(json.dumps(MODRINTH_INDEX, indent=4))

        archiveFolder(directory, MODPACK_FILENAME)

    def mserver(directory):
        if os.path.isdir(os.path.join("server")): return

        downloadFile(NEOFORGE_URL, os.path.join(directory, "neoforge.jar"))

        executeCommand(f"java -jar {os.path.join(directory, 'neoforge.jar')} --installServer {directory}")

        os.remove("neoforge.jar.log")

        os.makedirs("server", exist_ok=True)

        shutil.move(os.path.join(directory, "libraries"), os.path.join("server", "libraries"))

        shutil.move(os.path.join(directory, "run.bat"  ), os.path.join("server", "run.bat"  ))
        shutil.move(os.path.join(directory, "run.sh"   ), os.path.join("server", "run.sh"   ))

        run_lin = filterLines(readFile(os.path.join("server", "run.sh" )), "#"  ).strip()
        run_win = filterLines(readFile(os.path.join("server", "run.bat")), "REM").strip()

        run_win = "\n".join([line + (" nogui" if i == 1 and "nogui" not in line else "") for i, line in enumerate(run_win.split("\n"))])
        run_lin = "\n".join([line + (" nogui" if i == 0 and "nogui" not in line else "") for i, line in enumerate(run_lin.split("\n"))])

        writeToFile(os.path.join("server", "run.sh" ), run_lin)
        writeToFile(os.path.join("server", "run.bat"), run_win)

        writeToFile(os.path.join("server", "eula.txt"         ), f"eula=true"                 )
        writeToFile(os.path.join("server", "user_jvm_args.txt"), f"-Xmx{SERVER_MEMORY}"       )
        writeToFile(os.path.join("server", "server.properties"), f"motd={MODPACK_NAME} Server")

        os.makedirs(os.path.join("server", "mods"), exist_ok=True)

    with tempfile.TemporaryDirectory() as temp: modpack(temp) if args.client else None
    with tempfile.TemporaryDirectory() as temp: mserver(temp) if args.server else None

    for mod in (item for item in MOD_IDS_SERVER.items() if args.server):
        downloadMod(getModMetadata(*mod), os.path.join("server", "mods"))
