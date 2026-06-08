#!/usr/bin/env python3
import os
import sys
import base64
import json
import fnmatch
import requests
from typing import List, Set, Dict, Tuple

REPO_OWNER = "adhanushus19"
REPO_NAME = "Support-GPT-Enterprise"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# Default ignore list (in case .gitignore is missing or to supplement it)
DEFAULT_IGNORES = {
    ".git",
    ".github_dummy",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".pytest_cache",
    ".deepeval",
    "chromadb_store",
    ".coverage",
    "supportgpt.db",
    "dist",
    "build",
    "*.db",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
}

def load_gitignore(root_dir: str) -> List[str]:
    patterns = []
    gitignore_path = os.path.join(root_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns

def should_ignore(path: str, root_dir: str, gitignore_patterns: List[str]) -> bool:
    # Get path relative to the root_dir
    rel_path = os.path.relpath(path, root_dir).replace("\\", "/")
    if rel_path == ".":
        return False

    parts = rel_path.split("/")
    
    # Check if any parent directory or the file matches default ignore list
    for part in parts:
        if part in DEFAULT_IGNORES:
            return True
        for pattern in DEFAULT_IGNORES:
            if "/" not in pattern and fnmatch.fnmatch(part, pattern):
                return True

    # Check gitignore patterns
    for pattern in gitignore_patterns:
        # Normalize pattern
        p = pattern.rstrip("/")
        # If pattern starts with /, match from root
        if pattern.startswith("/"):
            if fnmatch.fnmatch(rel_path, p[1:]) or fnmatch.fnmatch(rel_path + "/", p[1:] + "/"):
                return True
        else:
            # Match anywhere in path
            if fnmatch.fnmatch(rel_path, p) or any(fnmatch.fnmatch(part, p) for part in parts):
                return True
            # Match directories
            if pattern.endswith("/"):
                if any(fnmatch.fnmatch(part + "/", p + "/") for part in parts):
                    return True

    return False

def get_all_files(root_dir: str, gitignore_patterns: List[str]) -> List[str]:
    upload_files = []
    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place to prevent os.walk from entering ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), root_dir, gitignore_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not should_ignore(file_path, root_dir, gitignore_patterns):
                upload_files.append(file_path)
    return upload_files

def get_remote_files(token: str) -> Dict[str, str]:
    """
    Returns a dict mapping remote file path to its SHA, by fetching the repo git tree.
    Returns empty dict if repo is empty or branch main does not exist yet.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    # Check default branch name (usually main or master)
    # First, get repo info
    r = requests.get(API_URL, headers=headers)
    if r.status_code == 404:
        print(f"Error: Repository {REPO_OWNER}/{REPO_NAME} not found or token invalid.")
        sys.exit(1)
    
    repo_info = r.json()
    default_branch = repo_info.get("default_branch", "main")
    
    # Get the latest commit on default branch to get tree sha
    ref_url = f"{API_URL}/git/ref/heads/{default_branch}"
    r = requests.get(ref_url, headers=headers)
    if r.status_code != 200:
        # Probably empty repository
        return {}
        
    ref_info = r.json()
    commit_sha = ref_info["object"]["sha"]
    
    # Get commit info
    commit_url = f"{API_URL}/git/commits/{commit_sha}"
    r = requests.get(commit_url, headers=headers)
    commit_info = r.json()
    tree_sha = commit_info["tree"]["sha"]
    
    # Get recursive tree
    tree_url = f"{API_URL}/git/trees/{tree_sha}?recursive=1"
    r = requests.get(tree_url, headers=headers)
    if r.status_code != 200:
        return {}
        
    tree_info = r.json()
    remote_files = {}
    for item in tree_info.get("tree", []):
        if item["type"] == "blob":
            remote_files[item["path"]] = item["sha"]
            
    return remote_files

def upload_file(token: str, local_path: str, rel_path: str, sha: str = None) -> bool:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    
    with open(local_path, "rb") as f:
        content_bytes = f.read()
    
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")
    
    url = f"{API_URL}/contents/{rel_path}"
    
    payload = {
        "message": f"upload: {rel_path}",
        "content": content_b64,
    }
    if sha:
        payload["sha"] = sha
        
    r = requests.put(url, headers=headers, json=payload)
    if r.status_code in (200, 201):
        return True
    else:
        print(f"\nFailed to upload {rel_path}: {r.status_code} - {r.text}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Upload codebase to GitHub using REST API.")
    parser.add_index = False
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--dry-run", action="store_true", help="Print files that would be uploaded without uploading")
    args = parser.parse_args()
    
    token = args.token or os.environ.get("GITHUB_TOKEN")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Project root: {root_dir}")
    
    gitignore_patterns = load_gitignore(root_dir)
    local_files = get_all_files(root_dir, gitignore_patterns)
    
    print(f"Found {len(local_files)} files to upload.")
    
    if args.dry_run:
        print("\n--- DRY RUN: Files to be uploaded ---")
        for f in local_files:
            rel = os.path.relpath(f, root_dir).replace("\\", "/")
            print(f"  {rel}")
        print("--------------------------------------")
        return
        
    if not token:
        print("Error: GitHub Personal Access Token is required. Use --token or set GITHUB_TOKEN environment variable.")
        sys.exit(1)
        
    print("Fetching remote repository file list to determine changes...")
    try:
        remote_files = get_remote_files(token)
        print(f"Found {len(remote_files)} existing files in the remote repository.")
    except Exception as e:
        print(f"Error checking remote repository: {e}")
        remote_files = {}

    success_count = 0
    failure_count = 0
    
    for idx, local_path in enumerate(local_files, 1):
        rel_path = os.path.relpath(local_path, root_dir).replace("\\", "/")
        
        # Check if remote already has this file and if we need to update it
        sha = remote_files.get(rel_path)
        
        # Show progress
        sys.stdout.write(f"\r[{idx}/{len(local_files)}] Uploading {rel_path}...")
        sys.stdout.flush()
        
        success = upload_file(token, local_path, rel_path, sha)
        if success:
            success_count += 1
        else:
            failure_count += 1
            
    print(f"\nUpload complete! Success: {success_count}, Failures: {failure_count}")

if __name__ == "__main__":
    main()
