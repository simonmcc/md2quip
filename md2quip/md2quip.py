"""Main module."""

import fnmatch
import os
import pprint
import urllib.error

import quipclient  # https://github.com/quip/quip-api/issues/38


def _filter_paths(basename, path, is_dir, exclude):
    """.gitignore style file filtering."""
    for item in exclude:
        # Items ending in '/' apply only to directories.
        if item.endswith('/') and not is_dir:
            continue
        # Items starting with '/' apply to the whole path.
        # In any other cases just the basename is used.
        match = path if item.startswith('/') else basename
        if fnmatch.fnmatch(match, item.strip('/')):
            return True
    return False


class md2quip(object):
    def __init__(self, quip_api_base_url, quip_api_access_token):
        self.quip_api_base_url = quip_api_base_url
        self.quip_api_access_token = quip_api_access_token

        self.quip_client = quipclient.QuipClient(
            access_token=self.quip_api_access_token, base_url=self.quip_api_base_url, request_timeout=120
        )

        # key=folder_id, value=name
        self._folder_cache = dict()

        # key=fully qualified path, value=folder_id
        self._path_cache = dict()

    def publish(self, files):
        # publish rendered docs to quip
        print(self.root_doc)
        user = self.quip_client.get_authenticated_user()
        print(f"Authenticated with Quip, user = {pprint.pformat(user)}")
        # doc = self.quip_client.new_document(self.root_doc)
        # pprint.pprint(doc)

        root_folder_id = 'JGMmOeQyhKz7'
        # simonmcc_folder_id = 'lsSCOCN4yaNw'

        sync_string = "<p>README.md - thread_id_1</p><p data-thread-id=abc123>CHANGELOG.md</p>"
        thread = self.quip_client.new_document(
            content=sync_string, title=".md2quip metadata", format='html', member_ids=[root_folder_id]
        )
        print(f"sync_string published as {pprint.pformat(thread)}")

        return

        # self.build_quip_folder_list()
        self._descend_into_folder(root_folder_id, self.quip_client, 0)

        for file in files:
            with open(file, 'r') as f:
                content = f.read()
                thread = self.quip_client.new_document(content=content, format='markdown', member_ids=[root_folder_id])
                print(f"Published {file} as {pprint.pformat(thread)}")

    def show_folders(self, thread_id=None, folder_id=None, depth=0):
        self._descend_into_folder(thread_id=thread_id, folder_id=folder_id, depth=depth, show_children=False)

    def show_folders_and_docs(self, thread_id=None, folder_id=None, depth=0, show_children=True):
        self._descend_into_folder(thread_id=None, folder_id=None, depth=0, show_children=False)

    def _descend_into_folder(self, thread_id=None, folder_id=None, depth=0, show_children=False):
        """folder_id & thread_id are not the same thing :("""

        if folder_id is None:
            # get the folder_id from the thread
            folder_id = self.quip_client.get_folder(thread_id).get("folder").get("id")

        print(f"\nDescending into {folder_id}")

        if folder_id in self._folder_cache:
            return

        self._folder_cache[folder_id] = ""

        try:
            folder = self.quip_client.get_folder(folder_id)
        except quipclient.QuipError as e:
            if e.code == 403:
                print("%sSkipped over restricted folder %s." % ("  " * depth, folder_id))
            else:
                print("%sSkipped over folder %s due to unknown error %d." % ("  " * depth, folder_id, e.code))
            return
        except urllib.error.HTTPError as e:
            print("%sSkipped over folder %s due to HTTP error %d." % ("  " * depth, folder_id, e.code))
            return

        title = folder["folder"].get("title", "Folder %s" % folder_id)
        print(f"Found folder {title} (depth={depth}, folder_id={folder_id})")

        self._folder_cache[folder_id] = folder
        print(f"_folder_cache keys: {self._folder_cache.keys()}")
        print(f"_folder_cache = {pprint.pformat(self._folder_cache)}")

        # self._path_cache
        if 'parent_id' in folder['folder']:
            parent_id = folder['folder']['parent_id']
            print(f"parent_id = {parent_id}")

            full_path = title
            while parent_id in self._folder_cache.keys():
                parent = self._folder_cache.get(parent_id).get('folder')
                print(f"parent = {pprint.pformat(parent)}")
                full_path = f"{parent.get('title')}/{full_path}"
                parent_id = parent.get('parent_id', None)

            self._path_cache[full_path] = folder_id
        else:
            self._path_cache[title] = folder_id

        print(f"self._path_cache = {pprint.pformat(self._path_cache)}")

        for child in folder["children"]:
            if "folder_id" in child:
                self._descend_into_folder(folder_id=child["folder_id"], depth=depth + 1)
            elif "thread_id" in child and show_children:
                thread = self.quip_client.get_thread(child["thread_id"])
                print(f"thread = {pprint.pformat(thread)}")

    def build_quip_folder_list(self, root_folder_id='JGMmOeQyhKz7'):
        root_folder = self.quip_client.get_folder(root_folder_id)

        for child in root_folder.get("children", []):
            child_folder_id = child.get("folder_id")
            child_thread_id = child.get("thread_id")
            if child_folder_id:
                child_details = self.quip_client.get_folder(child_folder_id)
                print(f"child_details = {pprint.pformat(child_details)}")
                self.build_quip_folder_list(root_folder_id=child_details['children'][0]['folder_id'])
            elif child_thread_id:
                child_details = self.quip_client.get_thread(child_thread_id)
                print(f"child_details = {pprint.pformat(child_details)}")

    def find_files(self, project_root="."):
        """Walk project_root and collect files to be published"""
        files = []
        include = ['*.md']
        exclude = ['.*', '/templates']

        for source_dir, dirnames, filenames in os.walk(project_root, followlinks=True):
            relative_dir = os.path.relpath(source_dir, project_root)

            for dirname in list(dirnames):
                path = os.path.normpath(os.path.join(relative_dir, dirname))
                # Skip any excluded directories
                if _filter_paths(basename=dirname, path=path, is_dir=True, exclude=exclude):
                    dirnames.remove(dirname)
            dirnames.sort()

            for filename in filenames:
                path = os.path.normpath(os.path.join(relative_dir, filename))
                # only collect the files that match filters
                if _filter_paths(basename=filename, path=path, is_dir=False, exclude=include):
                    files.append(path)

        return files
