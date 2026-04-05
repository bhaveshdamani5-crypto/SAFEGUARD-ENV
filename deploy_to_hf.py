
import os
import sys
from huggingface_hub import HfApi

def deploy():
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("Please set the HF_TOKEN environment variable.")
        print("You can get one from: https://huggingface.co/settings/tokens")
        sys.exit(1)

    api = HfApi(token=token)
    
    # Get username from token
    user = api.whoami()
    username = user['name']
    
    space_name = "safeguard-env"
    repo_id = f"{username}/{space_name}"
    
    try:
        print(f"Checking if Space {repo_id} exists...")
        api.space_info(repo_id)
        print("Space exists. Updating...")
    except Exception as e:
        print(f"Space doesn't exist. Creating new Space {repo_id}...")
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False
        )
        
    try:
        print("Uploading folder...")
        api.upload_folder(
            folder_path=".",
            repo_id=repo_id,
            repo_type="space",
            delete_patterns="*",
            ignore_patterns=["__pycache__/*", ".git/*", "deploy_to_hf.py", ".venv/*", ".env"]
        )
        print(f"Deployment complete! 🎉 Your space will be available at: https://huggingface.co/spaces/{repo_id}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to upload. Error: {e}")

if __name__ == "__main__":
    deploy()
