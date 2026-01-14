# import subprocess
# import tempfile
# import os
# from pathlib import Path


# class PiperTTS:
#     def __init__(self, piper_dir: str, model_path: str):
#         self.piper_exe = Path(piper_dir) / "piper.exe"
#         self.model_path = Path(model_path)

#         if not self.piper_exe.exists():
#             raise RuntimeError("❌ piper.exe not found")

#         if not self.model_path.exists():
#             raise RuntimeError("❌ Piper model not found")

#     def synthesize(self, text: str) -> bytes:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
#             wav_path = f.name

#         cmd = [
#             str(self.piper_exe),
#             "--model", str(self.model_path),
#             "--output_file", wav_path,
#             "--quiet",
#         ]

#         subprocess.run(
#             cmd,
#             input=text,
#             text=True,
#             check=True,
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL,
#         )

#         with open(wav_path, "rb") as f:
#             audio = f.read()

#         os.remove(wav_path)
#         return audio


import subprocess
import tempfile
import os
from pathlib import Path


class PiperTTS:
    def __init__(self, piper_dir: str, model_path: str):
        self.piper_exe = Path(piper_dir) / "piper.exe"
        self.model_path = Path(model_path)

        if not self.piper_exe.exists():
            raise RuntimeError("❌ piper.exe not found")

        if not self.model_path.exists():
            raise RuntimeError("❌ Piper model not found")

    def synthesize(self, text: str) -> bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav_path = f.name

        cmd = [
            str(self.piper_exe),
            "--model", str(self.model_path),
            "--output_file", wav_path,
            "--quiet",
        ]

        # 🔑 KEY FIX: send UTF-8 bytes, NOT text=True
        subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        with open(wav_path, "rb") as f:
            audio = f.read()

        os.remove(wav_path)
        return audio
