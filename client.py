import requests

SERVER_URL = "http://localhost:8000"

def send_image(path: str, save_to: str = "out.jpg"):
    """
    Envia uma imagem para /detect-image e grava o resultado em save_to.
    """
    with open(path, "rb") as f:
        files = {"file": (path, f, "image/jpeg")}
        resp = requests.post(f"{SERVER_URL}/detect-image", files=files)
    resp.raise_for_status()
    with open(save_to, "wb") as out:
        out.write(resp.content)
    print(f"Imagem anotada gravada em {save_to}")

def send_video(path: str, save_to: str = "out.mp4"):
    """
    Envia um vídeo para /detect-video e grava o resultado em save_to.
    """
    with open(path, "rb") as f:
        files = {"file": (path, f, "video/mp4")}
        resp = requests.post(f"{SERVER_URL}/detect-video", files=files, stream=True)
    resp.raise_for_status()
    with open(save_to, "wb") as out:
        for chunk in resp.iter_content(chunk_size=8192):
            out.write(chunk)
    print(f"Vídeo anotado gravado em {save_to}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python client.py [image|video] <input_path> [output_path]")
        sys.exit(1)

    mode, inp = sys.argv[1], sys.argv[2]
    outp = sys.argv[3] if len(sys.argv) > 3 else None

    if mode == "image":
        send_image(inp, save_to=outp or "annotated.jpg")
    elif mode == "video":
        send_video(inp, save_to=outp or "annotated.mp4")
    else:
        print("Modo inválido; use 'image' ou 'video'.")
