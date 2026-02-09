from pathlib import Path
from typing import List, Tuple
import shutil
import subprocess
import zipfile
from fastapi import UploadFile, HTTPException


class VideoProcessingGateway:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.uploads_dir = base_dir / "uploads"
        self.outputs_dir = base_dir / "outputs"
        self.temp_dir = base_dir / "temp"

        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, upload_file: UploadFile, timestamp: str) -> Path:
        filename = f"{timestamp}_{upload_file.filename}"
        dest = self.uploads_dir / filename
        try:
            with open(dest, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        finally:
            upload_file.file.close()

        return dest

    def _create_zip(self, files: List[Path], zip_path: Path) -> None:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in files:
                zipf.write(f, arcname=f.name)

    def process_video(self, video_path: Path, timestamp: str, fps: int = 1) -> Tuple[Path, int, List[str]]:
        proc_temp = self.temp_dir / timestamp
        proc_temp.mkdir(parents=True, exist_ok=True)

        frame_pattern = str(proc_temp / "frame_%04d.png")
        cmd = [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vf",
            f"fps={fps}",
            "-y",
            frame_pattern,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            try:
                shutil.rmtree(proc_temp)
            except Exception:
                pass
            raise HTTPException(status_code=500, detail=f"ffmpeg error: {result.stderr}")

        frames = sorted(proc_temp.glob("*.png"))
        if not frames:
            shutil.rmtree(proc_temp)
            raise HTTPException(status_code=500, detail="Nenhum frame extraído do vídeo")

        zip_filename = f"frames_{timestamp}.zip"
        zip_path = self.outputs_dir / zip_filename
        self._create_zip(frames, zip_path)

        image_names = [f.name for f in frames]

        try:
            shutil.rmtree(proc_temp)
        except Exception:
            pass

        return zip_path, len(frames), image_names
