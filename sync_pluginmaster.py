#!/usr/bin/env python3
import json
import time
from urllib.request import Request, urlopen


REPOSITORY = "hu1j1233/Questionable"
UPSTREAM_REPOSITORY = "PunishXIV/Questionable"
PLUGINMASTER = "pluginmaster.json"


def get_json(url):
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "hu1j1233-DalamudPlugins",
        },
    )
    with urlopen(request) as response:
        return json.load(response)


def choose_releases(releases):
    stable = next((release for release in releases if not release["draft"] and not release["prerelease"]), None)
    testing = next((release for release in releases if not release["draft"] and release["prerelease"]), stable)
    if stable is None:
        raise RuntimeError("Questionable has no published stable release")
    return stable, testing


def release_asset(release, name):
    asset = next((asset for asset in release["assets"] if asset["name"] == name), None)
    if asset is None:
        raise RuntimeError(f"Release {release['tag_name']} has no {name} asset")
    return asset["browser_download_url"]


def upstream_version():
    release = get_json(f"https://api.github.com/repos/{UPSTREAM_REPOSITORY}/releases/latest")
    return release["tag_name"]


def manifest_entry(stable, testing, releases):
    stable_manifest = get_json(release_asset(stable, "Questionable.json"))
    testing_manifest = get_json(release_asset(testing, "Questionable.json"))
    source_version = upstream_version()
    download_count = sum(
        asset["download_count"]
        for release in releases
        for asset in release["assets"]
    )

    return {
        "Author": "hu1j1233",
        "Name": "Questionable",
        "Punchline": "中文本地化的任务助手。",
        "Description": f"Questionable 的中文本地化版本，基于上游 Questionable {source_version}，帮助你自动完成支持的任务。",
        "InternalName": "Questionable",
        # Release tags may carry a human-facing build suffix that is not a
        # valid Dalamud/.NET assembly version. Always publish the version
        # produced by the plugin manifest instead.
        "AssemblyVersion": stable_manifest["AssemblyVersion"],
        "TestingAssemblyVersion": testing_manifest["AssemblyVersion"],
        "DalamudApiLevel": stable_manifest["DalamudApiLevel"],
        "TestingDalamudApiLevel": testing_manifest["DalamudApiLevel"],
        "DownloadLinkInstall": release_asset(stable, "latest.zip"),
        "DownloadLinkUpdate": release_asset(stable, "latest.zip"),
        "DownloadLinkTesting": release_asset(testing, "latest.zip"),
        "RepoUrl": f"https://github.com/{REPOSITORY}",
        "IconUrl": stable_manifest.get("IconUrl", "https://puni.sh/api/plugins/icon/94"),
        "Tags": ["quests", "msq", "cn"],
        "ApplicableVersion": "any",
        "LoadPriority": 0,
        "AcceptsFeedback": True,
        "DownloadCount": download_count,
        "LastUpdate": int(time.time()),
        "Changelog": stable.get("body") or "",
    }


def main():
    releases = get_json(f"https://api.github.com/repos/{REPOSITORY}/releases")
    stable, testing = choose_releases(releases)
    document = [manifest_entry(stable, testing, releases)]
    with open(PLUGINMASTER, "w", encoding="utf-8", newline="\n") as file:
        json.dump(document, file, ensure_ascii=False, indent=2)
        file.write("\n")


if __name__ == "__main__":
    main()
