import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Awaitable, Any, Dict, Tuple, List
import httpx
from packaging.version import Version, InvalidVersion


def async_ttl_cache(ttl: int):
    cache: Dict[str, Tuple[float, Any]] = {}

    def decorator(func: Callable[[str], Awaitable[Any]]):
        @wraps(func)
        async def wrapper(arg: str):
            now = time.time()
            if arg in cache:
                timestamp, result = cache[arg]
                if now - timestamp < ttl:
                    return result
            result = await func(arg)
            cache[arg] = (now, result)
            return result

        return wrapper

    return decorator


def is_non_production_version(version: str) -> bool:
    return any(part in version for part in ["a", "b", "rc", "dev"])


def is_production_version(version_str: str) -> bool:
    try:
        v = Version(version_str)
        return not v.is_prerelease and not v.is_devrelease
    except InvalidVersion:
        raise ValueError(f"Invalid version string: {version_str}")


@async_ttl_cache(ttl=3600)
async def fetch_releases_from_github(repo_url: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(repo_url)
        response.raise_for_status()
        return response.json()


@dataclass
class GitHubRelease:
    version: str
    notes: str
    url: str
    is_pre_release: bool
    is_production: bool = False

    def __post_init__(self):
        self.is_production = is_production_version(self.version)


async def fetch_newer_releases(
    repo_url: str,
    current_version_str: str,
    include_pre_releases: bool = True,
) -> List[GitHubRelease]:
    try:
        releases = await fetch_releases_from_github(repo_url)
        current = Version(current_version_str)
        newer_releases: List[GitHubRelease] = []

        for release in releases:
            tag = release.get("tag_name", "").lstrip("v")
            try:
                release_version = Version(tag)
            except InvalidVersion:
                continue

            if release_version > current and (
                include_pre_releases or not release_version.is_prerelease
            ):
                newer_releases.append(
                    GitHubRelease(
                        version=str(release_version),
                        notes=release.get("body") or "No release notes provided.",
                        url=release.get("html_url"),
                        is_pre_release=release.get("prerelease", False),
                    )
                )
        return newer_releases

    except Exception as e:
        print(f"Failed to fetch releases: {e}")
