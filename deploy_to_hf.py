import os
from huggingface_hub import HfApi

def deploy_to_spaces():
    # HF token should be set as an environment variable HF_TOKEN, or passed directly below
    # Make sure you are logged in via `huggingface-cli login` or provide the token.
    token = os.environ.get("HF_TOKEN")
    
    if not token:
        print("Please enter your Hugging Face Token (starts with 'hf_...').")
        print("You can get one from: https://huggingface.co/settings/tokens")
        token = input("HF Token: ").strip()

    print("\nPreparing to deploy to Hugging Face...")
    
    api = HfApi()
    repo_id = "bhavesh657/SafeGuard-Env"
    
    try:
        print(f"Uploading files to Space '{repo_id}'...")
        
        # Upload the entire current folder excluding useless local stuff
        api.upload_folder(
            folder_path=".",
            repo_id=repo_id,
            repo_type="space",
            token=token,
            ignore_patterns=[
                ".venv/*", 
                ".git/*", 
                "__pycache__/*", 
                "*.pyc",
                "docs/*",
                ".env"
            ],
            commit_message="feat: Deploy OpenEnv Gym RL architecture"
        )
        print("\n✅ Deployment Successful!")
        print(f"Your Hackathon App is now live at: https://huggingface.co/spaces/{repo_id}")
    
    except Exception as e:
        print(f"\n❌ Deployment Failed: {e}")

if __name__ == "__main__":
    deploy_to_spaces()
