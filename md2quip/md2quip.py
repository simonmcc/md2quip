"""Main module."""

import fnmatch
import logging
import os
import pprint
import urllib.error
from urllib.parse import urlparse

import quipclient  # https://github.com/quip/quip-api/issues/38

logger = logging.getLogger(__name__)


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
    def __init__(
        self, quip_root, project_root='.', quip_api_base_url=None, quip_api_access_token=None, quip_client=None
    ):

        if quip_api_base_url is not None and quip_api_access_token is not None:
            self.quip_api_base_url = quip_api_base_url
            self.quip_api_access_token = quip_api_access_token

            self.quip_client = quipclient.QuipClient(
                access_token=self.quip_api_access_token, base_url=self.quip_api_base_url, request_timeout=120
            )
        elif quip_client is not None:
            self.quip_client = quip_client
        else:
            raise Exception("No Quip API access provided")

        self.quip_root_url = quip_root
        self.project_root = project_root

        # key=folder_id, value=name
        self._folder_cache = dict()

        # key=thread_id, value=thread as a dict
        self._thread_cache = dict()

        # key=fully qualified path, value=folder_id
        self._path_cache = dict()

    def get_root_folder_id(self):
        """convert the quip_root URL (or partial URL or prefix_id) into a proper thread_id
        Quip folder_id & thread_id are not the same thing :(
        The id you see on a URL isn't a thread_id or a folder_id, but can be used as a thread_id for a
        one-way lookup to find the actual thread_id."""
        logger.debug(f"Extracting secret_path from {self.quip_root_url}")
        url = urlparse(self.quip_root_url)
        secret_path = url.path.split('/')[1]
        logger.debug(f"Converting {secret_path} to a folder_id")
        folder = self.quip_client.get_folder(secret_path)
        self.quip_root_folder_id = folder.get('folder').get('id')
        logger.debug(f"root folder = {pprint.pformat(self.quip_root_folder_id)}")

    def find_thread_by_title(self, root_id, title):
        # prime our cache of folders & threads
        self._descend_into_folder(folder_id=self.quip_root_folder_id, show_children=True)

        logger.info(pprint.pformat(self._thread_cache))

        return 'FHcAAAgmJDW'

    def get_metadata_thread(self):
        """Find or create a metadata thread"""
        metadata_title = ".md2quip metadata"
        sync_string = "<p>README.md - thread_id_1</p><p data-thread-id=abc123>CHANGELOG.md</p>"
        metadata_thread_id = self.find_thread_by_title(self.quip_root_folder_id, metadata_title)

        if metadata_thread_id is None:
            thread = self.quip_client.new_document(
                content=sync_string, title=".md2quip metadata", format='html', member_ids=[self.quip_root_folder_id]
            )
            logger.info(f"sync_string published as {pprint.pformat(thread)}")
        else:
            logger.error('TODO: Update existing thread')

        return

    def publish(self, files, root_folder_id):
        # publish rendered docs to quip
        metadata_title = ".md2quip metadata"

        sync_string = "<p>README.md - thread_id_1</p><p data-thread-id=abc123>CHANGELOG.md</p>"
        metadata_thread_id = self.find_thread_by_title(root_folder_id, metadata_title)

        if metadata_thread_id is None:
            thread = self.quip_client.new_document(
                content=sync_string, title=".md2quip metadata", format='html', member_ids=[root_folder_id]
            )
            logger.info(f"sync_string published as {pprint.pformat(thread)}")
        else:
            logger.error('TODO: Update existing thread')

        return

        # self.build_quip_folder_list()
        self._descend_into_folder(root_folder_id, self.quip_client, 0)

        for file in files:
            with open(file, 'r') as f:
                content = f.read()
                thread = self.quip_client.new_document(content=content, format='markdown', member_ids=[root_folder_id])
                print(f"Published {file} as {pprint.pformat(thread)}")

    def show_folders(self):
        self.get_root_folder_id()
        self._descend_into_folder(folder_id=self.quip_root_folder_id, depth=0, show_children=False)

    def show_folders_and_docs(self, depth=0):
        self.get_root_folder_id()
        self._descend_into_folder(folder_id=self.quip_root_folder_id, depth=0, show_children=True)

    def _descend_into_folder(self, folder_id, depth=0, show_children=False):
        logger.debug(f"_descend_into_folder(folder_id={folder_id}, depth={depth}, show_children={show_children}")
        logger.info(f"\nDescending into {folder_id}")

        if folder_id in self._folder_cache:
            return

        self._folder_cache[folder_id] = ""

        try:
            folder = self.quip_client.get_folder(folder_id)
        except quipclient.QuipError as e:
            if e.code == 403:
                logger.warn("%sSkipped over restricted folder %s." % ("  " * depth, folder_id))
            else:
                logger.warn("%sSkipped over folder %s due to unknown error %d." % ("  " * depth, folder_id, e.code))
            return
        except urllib.error.HTTPError as e:
            logger.error("%sSkipped over folder %s due to HTTP error %d." % ("  " * depth, folder_id, e.code))
            return

        title = folder["folder"].get("title", "Folder %s" % folder_id)
        logger.info(f"Found folder {title} (depth={depth}, folder_id={folder_id})")

        self._folder_cache[folder_id] = folder
        logger.debug(f"_folder_cache keys: {self._folder_cache.keys()}")
        logger.debug(f"_folder_cache = {pprint.pformat(self._folder_cache)}")

        # self._path_cache
        if 'parent_id' in folder['folder']:
            parent_id = folder['folder']['parent_id']
            logger.debug(f"parent_id = {parent_id}")

            full_path = title
            while parent_id in self._folder_cache.keys():
                parent = self._folder_cache.get(parent_id).get('folder')
                logger.debug(f"parent = {pprint.pformat(parent)}")
                full_path = f"{parent.get('title')}/{full_path}"
                parent_id = parent.get('parent_id', None)

            self._path_cache[full_path] = folder_id
        else:
            self._path_cache[title] = folder_id

        logger.debug(f"\nself._path_cache = \n{pprint.pformat(self._path_cache)}")

        for child in folder["children"]:
            if "folder_id" in child:
                self._descend_into_folder(folder_id=child["folder_id"], depth=depth + 1, show_children=show_children)
            elif "thread_id" in child and show_children:
                if child["thread_id"] not in self._thread_cache.keys():
                    thread = self.quip_client.get_thread(child["thread_id"])
                    self._thread_cache[child["thread_id"]] = thread
                logger.debug(f"thread = {pprint.pformat(thread)}")

    def build_quip_folder_list(self, root_folder_id='JGMmOeQyhKz7'):
        root_folder = self.quip_client.get_folder(root_folder_id)

        for child in root_folder.get("children", []):
            child_folder_id = child.get("folder_id")
            child_thread_id = child.get("thread_id")
            if child_folder_id:
                child_details = self.quip_client.get_folder(child_folder_id)
                logger.debug(f"child_details = {pprint.pformat(child_details)}")
                self.build_quip_folder_list(root_folder_id=child_details['children'][0]['folder_id'])
            elif child_thread_id:
                child_details = self.quip_client.get_thread(child_thread_id)
                logger.debug(f"child_details = {pprint.pformat(child_details)}")

    def find_files(self):
        """Walk project_root and collect files to be published"""
        files = []
        include = ['*.md']
        exclude = ['.*', '/templates']

        for source_dir, dirnames, filenames in os.walk(self.project_root, followlinks=True):
            relative_dir = os.path.relpath(source_dir, self.project_root)

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
