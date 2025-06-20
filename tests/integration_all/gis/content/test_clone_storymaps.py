import os
import json
import uuid
import tempfile
import unittest
from utils.decorators import integration_test, from_to_profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()
storymap_item_data = {
    "nodes": {
        "n-1A6t0x": {
            "config": {"isHidden": True},
            "data": {"links": []},
            "type": "navigation",
        },
        "n-5cQmXv": {"data": {"text": "", "type": "paragraph"}, "type": "text"},
        "n-QUJ38D": {"data": {"text": "", "type": "h4"}, "type": "text"},
        "n-UShiLa": {"data": {"attribution": "", "content": ""}, "type": "attribution"},
        "n-j1nNRk": {
            "data": {
                "byline": "unittest",
                "summary": "blah blah",
                "title": "Test Storymap",
                "titlePanelPosition": "start",
                "type": "minimal",
            },
            "type": "storycover",
        },
        "n-rq4f0s": {
            "children": ["n-j1nNRk", "n-1A6t0x", "n-zPc9Ve"],
            "config": {"coverDate": "first-published"},
            "data": {"storyTheme": "r-n91Njy"},
            "type": "story",
        },
        "n-zPc9Ve": {
            "children": ["n-QUJ38D", "n-5cQmXv", "n-UShiLa"],
            "type": "credits",
        },
    },
    "resources": {
        "r-n91Njy": {
            "data": {"themeBaseVariableOverrides": {}, "themeId": "summit"},
            "type": "story-theme",
        }
    },
    "root": "n-rq4f0s",
}


@from_to_profiles.all_except_k8s
@integration_test
class TestStoryMapCloning(unittest.TestCase):
    """Tests clone items for storymaps (2.0)"""

    def setUp(self):
        self.folder = self.from_gis.content.folders._get_or_create(
            folder="integration_testing_gis_content_clone_storymap",
            owner=self.from_gis._username,
        )

    def test_clone_storymap_draft(self):
        """tests cloning storymap in draft mode: agol <--> ent"""
        text_data = json.dumps(storymap_item_data)
        item = self.folder.add(
            {
                "type": "StoryMap",
                "tags": "integration_testing",
                "title": f"Test Storymap Clone {uuid.uuid4().hex[:5]}",
                "description": "story_map.description",
                "typeKeywords": [
                    "arcgis-storymaps",
                    "smdraftresourceid:draft_1616064052930.json",
                    "smfirstpublisheddate:1616064052928",
                    "smpublisheddate:1616064052928",
                    "smstatuspublished",
                    "smversiondraft:21.11.0",
                    "smversionpublished:21.11.0",
                    "StoryMap",
                    "Web Application",
                ],
                "text": text_data,
            }
        ).result()

        with tempfile.TemporaryDirectory() as path:
            draft_file = os.path.join(path, "draft_1616064052930.json")
            with open(draft_file, "w") as writer:
                writer.write(text_data)
            rm = item.resources
            rm.add(file=draft_file, file_name="draft_1616064052930.json")

        gis_dest = self.to_gis
        result = gis_dest.content.clone_items([item])
        item.delete(permanent=True)
        assert isinstance(result, list)
        assert result[0].type == "StoryMap"
        assert result[0].url is None
        assert len(result[0].resources.list()) > 0
        assert result[0].delete(permanent=True)

    def test_clone_storymap(self):
        """tests cloning storymap: agol <--> ent"""
        text_data = json.dumps(storymap_item_data)
        item = self.folder.add(
            {
                "type": "StoryMap",
                "tags": "integration_testing",
                "title": f"Test Storymap Clone {uuid.uuid4().hex[:5]}",
                "description": "story_map.description",
                "typeKeywords": [
                    "arcgis-storymaps",
                    "smdraftresourceid:draft_1616064052930.json",
                    "smfirstpublisheddate:1616064052928",
                    "smpublisheddate:1616064052928",
                    "smstatuspublished",
                    "smversiondraft:21.11.0",
                    "smversionpublished:21.11.0",
                    "StoryMap",
                    "Web Application",
                ],
                "text": text_data,
            }
        ).result()

        item.update({"url": f"https://storymaps.arcgis.com/stories/{item.id}"})
        with tempfile.TemporaryDirectory() as path:
            draft_file = os.path.join(path, "draft_1616064052930.json")
            with open(draft_file, "w") as writer:
                writer.write(text_data)
            rm = item.resources
            rm.add(file=draft_file, file_name="draft_1616064052930.json")

        gis_dest = self.to_gis
        result = gis_dest.content.clone_items([item])
        item.delete(permanent=True)
        assert isinstance(result, list)
        assert result[0].type == "StoryMap"
        assert result[0].url
        assert len(result[0].resources.list()) > 0
        assert result[0].delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
