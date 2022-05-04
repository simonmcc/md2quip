# md2quip design

## general approach

Given a tree of MarkDown documents & Quip root, publish the found docs as nodes in quip.

* Quip nodes should be marked read-only
* Quip nodes should have a header/footer explaining that they are read-only as they are generated, with a link to the source repo
* Attempt to store metadata in Quip so that md2quip requires no independent data store.
    * root metadata would include original list of files published, so that when file is removed, we know to delete the quip copy of it
