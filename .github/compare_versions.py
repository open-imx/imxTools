import os
import sys
from packaging.version import Version, InvalidVersion

def main():
    current_version = os.getenv("CURRENT_VERSION")
    latest_release = os.getenv("LATEST_RELEASE")

    if not current_version:
        print("::error::CURRENT_VERSION is not set.")
        sys.exit(1)

    if latest_release == "none":
        print("No previous release found. Proceeding to release.")
        print("SHOULD_RELEASE=true")
        return

    try:
        v_current = Version(current_version)
        v_latest = Version(latest_release)
    except InvalidVersion as e:
        print(f"::error::Invalid version format: {e}")
        sys.exit(1)

    if v_current > v_latest:
        print("Current version is newer. Proceeding to release.")
        print("SHOULD_RELEASE=true")
    elif v_current != v_latest:
        print("Versions differ but not newer (possible pre-release downgrade). Proceeding to release.")
        print("SHOULD_RELEASE=true")
    elif v_current == v_latest:
        print("Current version is same as released. Skipping release.")
        print("SHOULD_RELEASE=false")
    else:
        print("Current version is not newer. Skipping release.")
        print("SHOULD_RELEASE=false")

if __name__ == "__main__":
    main()
