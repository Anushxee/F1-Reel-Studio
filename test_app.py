"""Fast smoke tests that do not require a video file, network access, or API key."""
from pathlib import Path
import tempfile
import unittest

from agents.metadata import create_metadata
from agents.reel_builder import write_ass_overlay, write_srt
from agents.transcription import CaptionCue


class ReelStudioSmokeTests(unittest.TestCase):
    def test_offline_metadata_has_publish_basics(self) -> None:
        metadata = create_metadata("", "A last-lap overtake", use_ai=False)
        self.assertIn("#F1", metadata["hashtags"])
        self.assertIn("last-lap", metadata["caption"])

    def test_caption_srt_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "caption.srt"
            result = write_srt("A short caption for the reel", 8, target)
            self.assertEqual(result, target)
            self.assertIn("00:00:08,000", target.read_text(encoding="utf-8"))

    def test_word_timed_brand_overlay_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "overlay.ass"
            result = write_ass_overlay(
                [CaptionCue(0.1, 0.4, "Wheel"), CaptionCue(0.5, 0.9, "to wheel")],
                5,
                target,
                "Last lap chaos",
                "@f1studio",
                "Race Red",
            )
            contents = target.read_text(encoding="utf-8-sig")
            self.assertEqual(result, target)
            self.assertIn("Last lap chaos", contents)
            self.assertIn("WHEEL", contents)


if __name__ == "__main__":
    unittest.main()
