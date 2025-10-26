#!/bin/bash

# git_sync.sh - Create a branch, commit and sync changes, then return to main
#
# Usage:
#   ./git_sync.sh [branch_name]
#
# If no branch name is provided, defaults to: branch_YYYY-MM-DD
#
# Note: If you get credential errors, you may need to configure git credentials:
#   git config --global credential.helper store
#   or use SSH keys instead of HTTPS

set -e  # Exit on error

# Use provided branch name or generate default with current date
if [ -z "$1" ]; then
  branch_name="branch_$(date +%Y-%m-%d)"
  echo "No branch name provided. Using default: $branch_name"
else
  branch_name="$1"
fi

echo "=================================="
echo "Git Sync Script"
echo "Target branch: $branch_name"
echo "=================================="

# Ensure we're on main branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ]; then
  echo "Warning: Currently on branch '$current_branch'. Switching to main first..."
  git checkout main
fi

# Fetch the latest updates from the remote repository
echo "Fetching latest updates from remote..."
if ! git fetch 2>&1; then
  echo "Warning: git fetch failed (possibly due to credential issues)."
  echo "Continuing anyway - this may cause issues if remote has been updated."
  echo "You may need to configure git credentials or use SSH keys."
fi

# Check if branch already exists locally
if git show-ref --verify --quiet "refs/heads/$branch_name"; then
  echo "Error: Branch '$branch_name' already exists locally."
  echo "Please choose a different branch name or delete the existing branch first."
  exit 1
fi

# Check if branch exists on remote
if git ls-remote --heads origin "$branch_name" 2>/dev/null | grep -q "$branch_name"; then
  echo "Error: Branch '$branch_name' already exists on remote."
  echo "Please choose a different branch name or delete the remote branch first."
  exit 1
fi

# Add and commit any untracked or modified files with a generic commit message
if [ -n "$(git status --porcelain)" ]; then
  echo "Uncommitted changes detected. Adding and committing..."
  git add .
  git commit -m "WIP: Auto-commit changes before creating branch '$branch_name'"
  
  # Push committed changes on main to the remote
  echo "Pushing changes to main..."
  if ! git push 2>&1; then
    echo "Error: Failed to push to main. You may need to push manually."
    echo "Run: git push origin main"
    exit 1
  fi
else
  echo "No uncommitted changes detected."
fi

# Create and switch to the new branch
echo "Creating and switching to branch '$branch_name'..."
git checkout -b "$branch_name"

# Push the new branch to the remote
echo "Pushing branch '$branch_name' to remote..."
if ! git push -u origin "$branch_name" 2>&1; then
  echo "Error: Failed to push branch to remote."
  echo "The branch has been created locally but not pushed."
  echo "You can try pushing manually: git push -u origin $branch_name"
  git checkout main
  exit 1
fi

# Switch back to the main branch
echo "Switching back to main..."
git checkout main

echo "=================================="
echo "✓ Success!"
echo "Branch '$branch_name' created and pushed to remote."
echo "You are now back on 'main'."
echo "=================================="
