import os
import sys
from packaging.version import Version, InvalidVersion

def main():
    current_version = os.getenv("CURRENT_VERSION")
    latest_release = os.getenv("LATEST_RELEASE")
    mode = os.getenv("MODE", "enforce").lower()

    if not current_version:
        print("::error::Missing CURRENT_VERSION")
        sys.exit(1)

    if not latest_release or latest_release == "none":
        print("No previous release found. Proceeding to release.")
        print("SHOULD_RELEASE=true")
        return

    try:
        v_current = Version(current_version)
        v_latest = Version(latest_release)
    except InvalidVersion as e:
        print(f"::error::Invalid version format: {e}")
        sys.exit(1)

    if mode == "release":
        if v_current != v_latest:
            print("SHOULD_RELEASE=true")
        else:
            print("SHOULD_RELEASE=false")
            print("::error::🚫 Current version is same as latest release.")
            sys.exit(1)
    elif mode == "enforce":
        if v_current > v_latest:
            print("SHOULD_RELEASE=true")
        elif v_current == v_latest:
            print("SHOULD_RELEASE=false")
            print("::error::🚫 Version has not been bumped.")
            sys.exit(1)
        else:
            print("SHOULD_RELEASE=false")
            print(f"::error::🚫 Version is older than baseline ({v_current} < {v_latest}).")
            sys.exit(1)
    else:
        print(f"::error::Unsupported MODE value: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
