import requests
import feedparser

# URL of the releases.atom feed for the repository
repo_url = "https://github.com/bubfusion/Vatsim-Discord-RPC/releases.atom"

def check_for_update(version):
  # Fetch the releases.atom feed
  response = requests.get(repo_url)

  if response.status_code == 200:
      # Parse the Atom feed
      feed = feedparser.parse(response.content)
      
      # Get the latest release entry
      latest_release = feed.entries[0]
      
      # Extract the ID of the latest release
      latest_release_id = latest_release.id
      
      latest_release_version = latest_release_id.split("/")[-1]
      
      # Compare the IDs
      if version == latest_release_version:
          return True
      else:
          return False
  else:
      return None