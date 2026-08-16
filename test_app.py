"""Fast smoke tests that do not require a video file, network access, or API key."""
from pathlib import Path
import tempfile
import unittest

from agents.metadata import create_metadata
from agents.reel_builder import write_srt


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


if __name__ == "__main__":
    unittest.main()
