import sys

## Uncomment if running locally without install and update path
##
##sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_5988\src")
##

import os
import json
import uuid
import logging
import tempfile
import unittest
from arcgis.gis import GIS

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

storymap_item_data = {'nodes': {'n-1A6t0x': {'config': {'isHidden': True},
                        'data': {'links': []},
                        'type': 'navigation'},
           'n-5cQmXv': {'data': {'text': '', 'type': 'paragraph'},
                        'type': 'text'},
           'n-QUJ38D': {'data': {'text': '', 'type': 'h4'}, 'type': 'text'},
           'n-UShiLa': {'data': {'attribution': '', 'content': ''},
                        'type': 'attribution'},
           'n-j1nNRk': {'data': {'byline': 'unittest',
                                 'summary': 'blah blah',
                                 'title': 'Test Storymap',
                                 'titlePanelPosition': 'start',
                                 'type': 'minimal'},
                        'type': 'storycover'},
           'n-rq4f0s': {'children': ['n-j1nNRk', 'n-1A6t0x', 'n-zPc9Ve'],
                        'config': {'coverDate': 'first-published'},
                        'data': {'storyTheme': 'r-n91Njy'},
                        'type': 'story'},
           'n-zPc9Ve': {'children': ['n-QUJ38D', 'n-5cQmXv', 'n-UShiLa'],
                        'type': 'credits'}},
 'resources': {'r-n91Njy': {'data': {'themeBaseVariableOverrides': {},
                                     'themeId': 'summit'},
                            'type': 'story-theme'}},
 'root': 'n-rq4f0s'}



class TestStoryMapCloning(unittest.TestCase):
    """Tests clone items for storymaps (2.0)"""
    def test_clone_agol_to_enterprise_draft(self):
        """tests cloning from agol to enterprise in draft mode"""
        text_data = json.dumps(storymap_item_data)
        gis_source = GIS(profile='your_online_profile', verify_cert=False, trust_env=True)

        item = gis_source.content.add({'type' : 'StoryMap',
                                 'tags' : 'tags',
                                 'title' : f'Test Storymap {uuid.uuid4().hex[:5]}',
                                 'description' : "story_map.description",
                                 'typeKeywords' : ['arcgis-storymaps',
                                                   'smdraftresourceid:draft_1616064052930.json',
                                                   'smfirstpublisheddate:1616064052928',
                                                   'smpublisheddate:1616064052928',
                                                   'smstatuspublished',
                                                   'smversiondraft:21.11.0',
                                                   'smversionpublished:21.11.0',
                                                   'StoryMap',
                                                   'Web Application'],

                                 'text' : text_data})
        with tempfile.TemporaryDirectory() as path:
            draft_file = os.path.join(path, 'draft_1616064052930.json')
            with open(draft_file, 'w') as writer:
                writer.write(text_data)
            rm = item.resources
            rm.add(file=draft_file, file_name='draft_1616064052930.json')

        gis_dest = GIS(profile='your_enterprise_profile', verify_cert=False, trust_env=True)
        result = gis_dest.content.clone_items([item])
        item.delete()
        assert isinstance(result, list)
        assert result[0].type == 'StoryMap'
        assert result[0].url is None
        assert len(result[0].resources.list()) > 0
        assert result[0].delete()

    def test_clone_agol_to_enterprise(self):
        """tests cloning from agol to enterprise"""
        text_data = json.dumps(storymap_item_data)
        gis_source = GIS(profile='your_online_profile', verify_cert=False, trust_env=True)

        item = gis_source.content.add({'type' : 'StoryMap',
                                 'tags' : 'tags',
                                 'title' : f'Test Storymap {uuid.uuid4().hex[:5]}',
                                 'description' : "story_map.description",
                                 'typeKeywords' : ['arcgis-storymaps',
                                                   'smdraftresourceid:draft_1616064052930.json',
                                                   'smfirstpublisheddate:1616064052928',
                                                   'smpublisheddate:1616064052928',
                                                   'smstatuspublished',
                                                   'smversiondraft:21.11.0',
                                                   'smversionpublished:21.11.0',
                                                   'StoryMap',
                                                   'Web Application'],

                                 'text' : text_data})
        item.update({'url' : f"https://storymaps.arcgis.com/stories/{item.id}"})
        with tempfile.TemporaryDirectory() as path:
            draft_file = os.path.join(path, 'draft_1616064052930.json')
            with open(draft_file, 'w') as writer:
                writer.write(text_data)
            rm = item.resources
            rm.add(file=draft_file, file_name='draft_1616064052930.json')

        gis_dest = GIS(profile='your_enterprise_profile', verify_cert=False, trust_env=True)
        result = gis_dest.content.clone_items([item])
        item.delete()
        assert isinstance(result, list)
        assert result[0].type == 'StoryMap'
        assert result[0].url
        assert len(result[0].resources.list()) > 0
        assert result[0].delete()

    def test_clone_ent_to_agol(self):
        """tests cloning from enterprise to ago"""
        text_data = json.dumps(storymap_item_data)
        gis_source = GIS(profile='your_enterprise_profile', verify_cert=False, trust_env=True)

        item = gis_source.content.add({'type' : 'StoryMap',
                                 'tags' : 'tags',
                                 'title' : f'Test Storymap {uuid.uuid4().hex[:5]}',
                                 'description' : "story_map.description",
                                 'typeKeywords' : ['arcgis-storymaps',
                                                   'smdraftresourceid:draft_1616064052930.json',
                                                   'smfirstpublisheddate:1616064052928',
                                                   'smpublisheddate:1616064052928',
                                                   'smstatuspublished',
                                                   'smversiondraft:21.11.0',
                                                   'smversionpublished:21.11.0',
                                                   'StoryMap',
                                                   'Web Application'],

                                 'text' : text_data})
        url = f"{gis_source._portal.url}/apps/storymaps/stories/{item.id}"
        item.update({'url' : url})
        with tempfile.TemporaryDirectory() as path:
            draft_file = os.path.join(path, 'draft_1616064052930.json')
            with open(draft_file, 'w') as writer:
                writer.write(text_data)
            rm = item.resources
            rm.add(file=draft_file, file_name='draft_1616064052930.json')

        gis_dest = GIS(profile='your_online_profile', verify_cert=False, trust_env=True)
        result = gis_dest.content.clone_items([item])
        item.delete()
        assert isinstance(result, list)
        assert result[0].type == 'StoryMap'
        assert result[0].url
        assert len(result[0].resources.list()) > 0
        assert result[0].delete()


if __name__ == "__main__":
    unittest.main()