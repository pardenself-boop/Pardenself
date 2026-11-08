"""Explicit GitHub release checks and hash-verified installer downloads.

No network request runs at import or automatically during workstation startup.
"""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

REPOSITORY = 'pardenself-boop/Pardenself'
API_URL = f'https://api.github.com/repos/{REPOSITORY}/releases?per_page=30'
MAX_INSTALLER_BYTES = 300 * 1024 * 1024


class HTTPSRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).scheme != 'https':
            raise ValueError('Update download redirected to an insecure connection')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_url(url):
    request = Request(url, headers={'User-Agent': 'BOOM-BAP-TOOLBOXX-Updater', 'Accept': 'application/vnd.github+json' if url == API_URL else 'application/octet-stream'})
    return build_opener(HTTPSRedirects()).open(request, timeout=20)


@dataclass(frozen=True)
class Update:
    build: str
    filename: str
    url: str
    sha256: str
    size: int
    prerelease: bool


def select_update(releases, current_build):
    if not isinstance(releases, list):
        raise ValueError('The update service returned an unexpected response')
    candidates = []
    for release in releases:
        if not isinstance(release, dict) or release.get('draft'):
            continue
        match = re.fullmatch(r'build-(\d{3,9})', release.get('tag_name', ''))
        if match and int(match[1]) > int(current_build):
            candidates.append((int(match[1]), match[1], release))
    if not candidates:
        return None
    _, build, release = max(candidates, key=lambda item: item[0])
    filename = f'BOOM_BAP_TOOLBOXX_Setup_{build}.exe'
    asset = next((item for item in release.get('assets', []) if item.get('name') == filename and item.get('state') == 'uploaded'), None)
    if asset is None:
        raise ValueError('The newest update does not have a complete Windows installer yet. Try again later.')
    expected_url = f'https://github.com/{REPOSITORY}/releases/download/build-{build}/{filename}'
    if asset.get('browser_download_url') != expected_url:
        raise ValueError('The installer is not hosted in the official TOOLBOXX release')
    size = asset.get('size')
    if type(size) is not int or not 2 <= size <= MAX_INSTALLER_BYTES:
        raise ValueError('The update has an invalid installer size')
    body_hash = re.search(r'SHA256:\s*`?([a-fA-F0-9]{64})(?![a-fA-F0-9])', release.get('body') or '')
    digest = asset.get('digest') or ''
    asset_hash = re.fullmatch(r'sha256:([a-fA-F0-9]{64})', digest)
    if not body_hash and not asset_hash:
        raise ValueError('The update has no SHA256 verification value. Download it from the release page instead.')
    if body_hash and asset_hash and body_hash[1].lower() != asset_hash[1].lower():
        raise ValueError('The update verification values disagree')
    sha256 = (asset_hash or body_hash)[1].lower()
    return Update(build, filename, expected_url, sha256, size, bool(release.get('prerelease')))


def check_for_update(current_build, opener=open_url):
    with opener(API_URL) as response:
        data = response.read(2 * 1024 * 1024 + 1)
    if len(data) > 2 * 1024 * 1024:
        raise ValueError('The update response is too large')
    return select_update(json.loads(data), current_build)


def verify_installer(path, update):
    path = Path(path)
    if path.stat().st_size != update.size:
        raise ValueError('Installer download is incomplete or has the wrong size')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        if stream.read(2) != b'MZ':
            raise ValueError('The download is not a Windows executable')
        stream.seek(0)
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != update.sha256:
        raise ValueError('Installer verification failed. The download will not be installed.')


def download_update(update, directory, progress=lambda done, total: None, opener=open_url):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix='toolboxx-', suffix='.partial', dir=directory)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, 'wb') as target, opener(update.url) as response:
            done = 0
            while True:
                block = response.read(256 * 1024)
                if not block:
                    break
                done += len(block)
                if done > update.size or done > MAX_INSTALLER_BYTES:
                    raise ValueError('The installer download exceeded its expected size')
                target.write(block)
                progress(done, update.size)
        verify_installer(temporary, update)
        destination = directory / update.filename
        os.replace(temporary, destination)
        return destination
    finally:
        temporary.unlink(missing_ok=True)
