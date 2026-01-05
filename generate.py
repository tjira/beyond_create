import json, os, requests, shutil, subprocess

MODPACK_NAME = "Beyond Create"
MINECRAFT_VERSION = "1.21.1"
NEOFORGE_VERSION = "21.1.217"
MODPACK_VERSION = "0.0.1"
SERVER_MEMORY = "4G"

NEOFORGE_URL = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{NEOFORGE_VERSION}/neoforge-{NEOFORGE_VERSION}-installer.jar"

MOD_IDS_SERVER = [
    "ZdLtebKH", # RHINO
    "8nuqyxbw", # KUBEJS
    "kztxpjAA", # APPLE SKIN
]

MOD_IDS_CLIENT = [
    "Pb3OXVqC", # SODIUM
    "xUpTkg0V", # XAEROS WORLD MAP
    "puXrtfcK", # XAEROS MINIMAP
    "t3ruzodq", # IRIS
]

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

def downloadFile(url, dest):
    with open(dest, "wb") as file: file.write(requests.get(url).content)

def executeCommand(command):
    subprocess.Popen(command, shell=True).communicate()

def getModMetadata(mod_id):
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

def writeToFile(filename, content):
    with open(filename, "w") as file: file.write(content + "\n")

if __name__ == "__main__":
    if os.path.exists("server"): shutil.rmtree("server")

    os.mkdir("server")
    os.chdir("server")

    downloadFile(NEOFORGE_URL, "neoforge.jar")
    executeCommand(f"java -jar neoforge.jar --installServer")

    writeToFile("eula.txt", "eula=true")
    writeToFile("user_jvm_args.txt", f"-Xmx{SERVER_MEMORY}")
    writeToFile("server.properties", f"motd={MODPACK_NAME} NeoForge Server")

    os.remove("neoforge.jar")
    os.remove("neoforge.jar.log")

    os.mkdir("mods")
    os.chdir("mods")

    for mod_id in MOD_IDS_SERVER:

        metadata = getModMetadata(mod_id)

        downloadFile(metadata["files"][0]["url"], metadata["files"][0]["filename"])

    os.chdir("..")
    os.chdir("..")

    if os.path.exists("modpack"): shutil.rmtree("modpack")

    os.mkdir("modpack")
    os.chdir("modpack")

    os.mkdir("overrides")

    for mod_id in MOD_IDS_SERVER + MOD_IDS_CLIENT:
        MODRINTH_INDEX["files"].append(generateModEntry(getModMetadata(mod_id)))

    open("modrinth.index.json", "w").write(json.dumps(MODRINTH_INDEX, indent=4))

    os.chdir("..")

    shutil.make_archive("modpack", 'zip', 'modpack')

    shutil.move("modpack.zip", f"{MODPACK_NAME.lower().replace(' ', '_')}_MC{MINECRAFT_VERSION}_v{MODPACK_VERSION}_client.mrpack")

    shutil.rmtree("modpack")
