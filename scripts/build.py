import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, check=True):
    print(f"\n[RUN] {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if check and result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    return result.returncode


def find_recipe_dirs(recipes_root: Path, target_pkg: str = None):
    dirs = []
    if not recipes_root.exists():
        return dirs

    for conanfile in recipes_root.rglob("conanfile.py"):
        if "test_package" in conanfile.parts:
            continue
        recipe_dir = conanfile.parent
        pkg_name = recipe_dir.parent.name if recipe_dir.name == "all" else recipe_dir.name
        if target_pkg and pkg_name != target_pkg:
            continue
        dirs.append((pkg_name, recipe_dir))
    return dirs


def should_skip(pkg_name: str, current_os: str) -> bool:
    # webkit2gtk is a Linux system package
    if pkg_name == "webkit2gtk" and current_os != "Linux":
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Build and optionally upload Conan packages.")
    parser.add_argument("--package", help="Specific package to build (builds all if omitted)")
    parser.add_argument("--user", default="", help="Conan user namespace (empty for standard naming)")
    parser.add_argument("--channel", default="", help="Conan channel (empty for standard naming)")
    parser.add_argument("--upload", action="store_true", help="Upload built packages to remote")
    parser.add_argument("--remote", default="gitlab", help="Conan remote name")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    recipes_dir = root_dir / "recipes"
    current_os = platform.system()

    all_recipes = find_recipe_dirs(recipes_dir)
    print(f"Current OS: {current_os}")
    print(f"Total available recipe(s) in repository: {len(all_recipes)}")

    # 1. First, export ALL valid recipes to local cache so local dependencies can be resolved
    print(f"\n{'='*50}\n[STEP 1] Pre-exporting all recipes to local cache\n{'='*50}")
    user_channel_args = []
    if args.user and args.channel:
        user_channel_args = [f"--user={args.user}", f"--channel={args.channel}"]

    for name, path in all_recipes:
        if should_skip(name, current_os):
            continue
        print(f"Exporting {name} ({path})...")
        run_cmd(["conan", "export", str(path)] + user_channel_args, check=True)

    # 2. Filter target recipes for build
    targets = find_recipe_dirs(recipes_dir, args.package)
    # Sort so that dependencies like webkit2gtk build before consumers like webview
    order_priority = {"webkit2gtk": 0, "elevate-kit": 1, "webview": 2}
    targets.sort(key=lambda x: order_priority.get(x[0], 99))

    built_packages = []

    print(f"\n{'='*50}\n[STEP 2] Building package(s)\n{'='*50}")
    for name, path in targets:
        if should_skip(name, current_os):
            print(f"\n[SKIP] Skipping {name} on {current_os} (unsupported OS)")
            continue

        print(f"\nBuilding {name} ({path})...")
        cmd = ["conan", "create", str(path)] + user_channel_args + ["--build=missing"]
        ret = run_cmd(cmd, check=False)
        if ret == 6:
            print(f"[SKIP] Invalid configuration for {name} on {current_os}, skipping.")
            continue
        elif ret != 0:
            print(f"[ERROR] Build failed for {name}")
            sys.exit(ret)
        built_packages.append(name)

    # 3. Upload built packages and recipes
    if args.upload and built_packages:
        print(f"\n{'='*50}\n[STEP 3] Uploading packages to remote '{args.remote}'\n{'='*50}")
        for name in built_packages:
            if args.user and args.channel:
                pattern = f"{name}/*@{args.user}/{args.channel}"
            else:
                pattern = f"{name}/*"
            print(f"Uploading {pattern}...")
            upload_cmd = ["conan", "upload", pattern, "-r", args.remote, "--confirm"]
            run_cmd(upload_cmd, check=True)


if __name__ == "__main__":
    main()
