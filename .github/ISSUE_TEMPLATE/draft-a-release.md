---
name: Draft a release
about: Use this to create the checklist needed for Python API release
title: "[RELEASE] "
labels: release
assignees: jyaistMap, rwmajor2, achapkowski, AtmaMani, rohitgeo, sandeepgadhwal, mohi9282,
  priyankatuteja, scdub

---

## About:
* This is the general to-do list for: **v 2.x release**, 
* Public availability is scheduled for : **<enter date>** 

### High level
   + [ ] Version milestone on Geosaurus repo -- **<enter url>**
   + [ ] Milestone on public doc repo -- **enter url**
   + [ ] Code freeze beings  -- **<enter date>** 
   + [ ] Doc freeze begins -- **<enter date>** 
   + [ ] Certification completion target date -- **<enter date>**
   + [ ] conda / pip / npm publish dates -- **<enter date>** 
   + [ ] Developers website deploy date --**<enter date>**
   + [ ] Developers website deploy milestone -- **<enter url>**

----

## Detailed Steps
### Doc and Website release
 - [ ] update [release notes](https://developers.arcgis.com/python/guide/release-notes/) page. Enter PR here: **<paste pr url>**
 - [ ] Review and merge doc PRs
 - [ ] Build new API ref files 
    - [ ] Merge API ref public SDK repo
    - [ ] Copy API ref files for DSX repo at `\\archive\CRData\Turing\python_api_ref`. (Use Windows OS) Reach out to Sara Sanchez
 - [ ] Publish new try-it-live enabled samples to [Geosaurus AGO group](https://www.arcgis.com/home/group.html?id=2464da88f55e45d89aedcae843167f51#overview)
- [ ] Tag SDK content from master on public repo [here](https://github.com/Esri/arcgis-python-api/releases) @AtmaMani

 - Developer's website
     - [ ] This issue tracks doc release on AFD repo: **<enter url>**
     - [ ] Create preview branch and build the site with new pages. This is the branch URL: **<enter url>**
     - [ ] Copy API ref files to `\\core.afd.geocloud.com\Core` for developers website. [See help on how to connect to this folder](https://docs.afd.geocloud.com/general/core-file-share/). Only use Windows OS for this. Do this on the Monday of the release, if you do it early, the files may be released too soon.     
     - [ ] This PR does merges all new SDK content for AFD release: **<enter pr url>**
     - [ ] Validate API ref on https://master-dev.developers.arcgis.com/python/api-reference/
     - [ ] Validate doc site on https://master-stage.developers.arcgis.com/python
     - [ ] Validate doc site on https://developers.arcgis.com/python
 
### Building Python packages
  - [ ] Tag on geosaurus the commit that triggered the build number release candidate. 
     - [ ] This is the final commit: **<paste commit url>**
     - [ ] This is the package build on zion: **<enter url or number>**
     - [ ] This is the tag on Geosaurus repo: **<enter tag url>**
 - [ ] Analyze if there any new dependencies. This issue tracks new deps: **<enter issue here>**
     - [ ] Update `environment.yml` with new deps for developer setups
     - [ ] Update `meta.yml` and `setup.py` to include new deps
     - [ ] Make lib inclusion requests. See [this folder for templates and examples](https://teams.microsoft.com/_#/files/General?threadId=19%3A0cdc273b0929434b953e2eaea338de71%40thread.skype&ctx=channel&context=3rd%2520party%2520lic%2520approval&rootfolder=%252Fsites%252FGeosaurus%252FShared%2520Documents%252FGeneral%252F3rd%2520party%2520lic%2520approval). Update Shaun Walbridge, Bill Major, Nicholas Giner.
 - [ ] bump version to **<enter version>** in both `meta.yaml`and `setup.py` (conda and pip), in `arcgis/__init__.py`
 - [ ] bump version in `doc/api_ref`
 - [ ] bump version in widgets/js/package.json (map widget)

### Publishing Python packages
  - [ ] post that build # conda package to esri channel. Version url: **<enter url>**
  - [ ] post that build # pip package to pypi.  Version url: **<enter url>**
  - [ ] publish the javascript widget package to npm.  Version url: **<enter url>**
-----

## Post release actions
  - [ ] Email Meena Spangurd about the release.
  - [ ] Email tech support to update product PLC
  - [ ] Publicize release via social media marketing channels. Reach out to **Lipika, Amy**. 
  - [ ] Optional - publish 'what's new' blog

Please forward this issue to anyone else who needs to be involved.
