import gradio as gr
from backend.storage import SecretStore
from encryption.crypto import AESCipher

cipher = AESCipher.from_env()
store = SecretStore(cipher=cipher)


def parse_env_text(text: str):
    store.clear()
    count = store.parse_env_content(text or "")
    previews = store.list_previews()
    rows = []
    for preview in previews:
        rows.append([
            preview.name,
            preview.masked_value,
            preview.current_version,
            preview.version_count,
            preview.risk_score,
            ", ".join(preview.leak_flags) or "none",
        ])
    return f"Encrypted {count} secret(s) with AES-256-GCM.", rows


def generate_token(secret_name: str, role: str) -> str:
    try:
        token = store.create_share_token(secret_name, role, ttl_seconds=1800)
        return f"Share token created for {secret_name}: {token.token}"
    except Exception as exc:
        return f"Error creating token: {exc}"


def scan_github_leaks(text: str) -> str:
    result = store.scan_text(text or "")
    cases = "; ".join(result.github_leak_cases) or "No leak patterns detected."
    return f"Risk: {result.risk_summary}\nDetails: {cases}"


def reset_workspace() -> str:
    store.clear()
    return "Workspace reset. Upload a new .env file to start secure sharing."


demo_description = "Upload a .env file to simulate encryption, versioning, token sharing, and GitHub leak detection."

with gr.Blocks(title="SafeGuard Env Demo", theme=gr.themes.Base()) as demo:
    gr.Markdown("# SafeGuard Env Demo")
    gr.Markdown(demo_description)

    with gr.Row():
        env_input = gr.Textbox(lines=10, label="Paste .env content", placeholder="API_KEY=abcd1234\nDATABASE_URL=postgres://user:pass@host/db")
        output = gr.Dataframe(
            headers=["Secret", "Masked", "Current", "Versions", "Risk", "Leak Flags"],
            datatype=["str", "str", "str", "str", "str", "str"],
            label="Encrypted Secret Preview",
        )

    with gr.Row():
        status = gr.Textbox(label="Status")
        leak_status = gr.Textbox(label="GitHub Leak Scan")

    encrypt_button = gr.Button("Encrypt & Preview")
    token_name = gr.Textbox(label="Secret Name for Sharing", placeholder="API_KEY")
    role_dropdown = gr.Dropdown(choices=["viewer", "editor", "admin"], value="viewer", label="Share Role")
    token_output = gr.Textbox(label="Token Output")
    token_button = gr.Button("Create Share Token")
    reset_button = gr.Button("Reset Workspace")

    encrypt_button.click(parse_env_text, inputs=[env_input], outputs=[status, output])
    token_button.click(generate_token, inputs=[token_name, role_dropdown], outputs=[token_output])
    env_input.change(scan_github_leaks, inputs=[env_input], outputs=[leak_status])
    reset_button.click(reset_workspace, outputs=[status])


def launch_demo():
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    launch_demo()
