import base64
import json
import unittest
import zipfile
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import path_setup
from tvart.validate import validate_tva
from tvart.render import compute_layout, ffmpeg_arguments, render_frame, render_tva
from tvart.core.text_frame import brightness_to_char
ROOT = Path(__file__).resolve().parent.parent

class RestartTests(unittest.TestCase):
    def test_common_layout(self):
        for c in json.loads((ROOT / "tests/fixtures/layout_cases.json").read_text()):
            self.assertEqual(list(compute_layout(c["columns"],c["rows"],c["width"],c["height"],c["fit"])), c["expected"])

    def test_common_conversion(self):
        for c in json.loads((ROOT / "tests/fixtures/conversion.json").read_text()):
            self.assertEqual(brightness_to_char(c["brightness"],c["charset"],c["invert"]),c["expected"])

    def test_ffmpeg_arguments_are_literal_and_silent(self):
        args=ffmpeg_arguments("ffmpeg",Path("frames with spaces"),Path("out.mp4"),15)
        self.assertIn("frames with spaces/%06d.png",args)
        self.assertIn("-an",args)
        self.assertIn("libx264",args)
        self.assertIn("-n",args)

    def test_png_dimensions_and_blocks(self):
        try:
            import cv2
        except ImportError:
            self.skipTest("OpenCV unavailable")
        image=render_frame([" █"],(32,16),fit="cover",fg="#ffffff",bg="#000000")
        self.assertEqual(image.shape,(16,32,3))
        self.assertEqual(int(image[8,8,0]),0)
        self.assertEqual(int(image[8,24,0]),255)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/ffprobe unavailable")
    def test_actual_mp4_media(self):
        try:
            import cv2
        except ImportError:
            self.skipTest("OpenCV unavailable")
        with TemporaryDirectory() as tmp:
            output=Path(tmp)/"card.mp4"
            fixture=json.loads((ROOT/"tests/fixtures/conformance/cases.json").read_text())
            manifest={**fixture["base"], "frame_count":3, "fps":10, "duration":0.3}
            archive=Path(tmp)/"input.tva"
            with zipfile.ZipFile(archive,"w") as z:
                z.writestr("manifest.json",json.dumps(manifest))
                for i in range(3):
                    z.writestr(f"frames/{i:06d}.txt","abc\ndef\n")
            self.assertEqual(render_tva(archive,output,format="mp4",size="64x32"),0)
            result=subprocess.run(["ffprobe","-v","error","-count_frames","-select_streams","v:0",
                "-show_entries","stream=codec_name,width,height,nb_read_frames:format=duration", "-of","json",str(output)],capture_output=True,text=True,check=True)
            probe=json.loads(result.stdout)
            stream=probe["streams"][0]
            self.assertEqual(stream["codec_name"],"h264")
            self.assertEqual((stream["width"],stream["height"]),(64,32))
            self.assertEqual(int(stream["nb_read_frames"]),3)
            self.assertAlmostEqual(float(probe["format"]["duration"]),0.3,places=1)
