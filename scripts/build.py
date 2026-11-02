import argparse
import os
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
        recipe_dir = conanfile.parent
        pkg_name = recipe_dir.parent.name if recipe_dir.name == "all" else recipe_dir.name
        if target_pkg and pkg_name != target_pkg:
            continue
        dirs.append((pkg_name, recipe_dir))
    return dirs


def main():
    parser = argparse.ArgumentParser(description="Build and optionally upload Conan packages.")
    parser.add_argument("--package", help="Specific package to build (builds all if omitted)")
    parser.add_argument("--user", default="xyz1001", help="Conan user namespace")
    parser.add_argument("--channel", default="stable", help="Conan channel")
    parser.add_argument("--upload", action="store_true", help="Upload built packages to remote")
    parser.add_argument("--remote", default="gitlab", help="Conan remote name")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    recipes_dir = root_dir / "recipes"

    found = find_recipe_dirs(recipes_dir, args.package)
    if not found:
        print(f"No recipe found in {recipes_dir}")
        return

    print(f"Found {len(found)} package recipe(s) to process:")
    for name, path in found:
        print(f"  - {name} at {path}")

    # Build each package
    for name, path in found:
        print(f"\n{'='*50}\nBuilding {name} ({path})\n{'='*50}")
        cmd = [
            "conan", "create", str(path),
            f"--user={args.user}",
            f"--channel={args.channel}",
            "--build=missing"
        ]
        run_cmd(cmd)

    # Upload if requested
    if args.upload:
        pattern = f"*/*@{args.user}/{args.channel}"
        print(f"\n{'='*50}\nUploading packages matching '{pattern}' to remote '{args.remote}'\n{'='*50}")
        upload_cmd = [
            "conan", "upload", pattern,
            "-r", args.remote,
            "--confirm"
        ]
        run_cmd(upload_cmd)


if __name__ == "__main__":
    main()
