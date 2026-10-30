name: Update M3U Playlist

on:
  schedule:
    # প্রতিদিন প্রতি ৬ ঘণ্টা পর পর স্বয়ংক্রিয়ভাবে চলবে
    - cron: '0 */6 * * *'
  workflow_dispatch: # ম্যানুয়ালি রান করার জন্য option

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Check out repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests beautifulsoup4

    - name: Run Scraping Script
      run: |
        python script.py

    - name: Commit and Push changes
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "github-actions[bot]@users.noreply.github.com"
        git add playlist.m3u
        git diff --quiet && git diff --staged --quiet || (git commit -m "Auto update playlist.m3u" && git push)

