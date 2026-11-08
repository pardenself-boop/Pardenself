import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from app_updates import check_for_update, download_update, select_update
from update_window import UpdateWindow

DATA = b'MZ' + b'toolboxx-test-installer' * 10
DIGEST = hashlib.sha256(DATA).hexdigest()


def release(build='063'):
    name = f'BOOM_BAP_TOOLBOXX_Setup_{build}.exe'
    return {'tag_name': 'build-' + build, 'draft': False, 'prerelease': True,
            'body': f'SHA256: `{DIGEST}`', 'assets': [{
                'name': name, 'size': len(DATA), 'state': 'uploaded',
                'browser_download_url': f'https://github.com/pardenself-boop/Pardenself/releases/download/build-{build}/{name}'}]}


class ReleaseSelectionTests(unittest.TestCase):
    def test_numeric_version_order_drafts_and_existing_version(self):
        draft = release('100'); draft['draft'] = True
        result = select_update([release('063'), release('064'), draft, release('061')], '062')
        self.assertEqual(result.build, '064')
        self.assertIsNone(select_update([release('062'), draft], '062'))

    def test_hash_can_come_from_github_asset_digest(self):
        item = release(); item['body'] = ''
        item['assets'][0]['digest'] = 'sha256:' + DIGEST
        self.assertEqual(select_update([item], '062').sha256, DIGEST)

    def test_missing_and_conflicting_hashes_block_installable_update(self):
        item = release(); item['body'] = ''
        with self.assertRaises(ValueError):select_update([item], '062')
        item['body'] = f'SHA256: `{DIGEST}`'
        item['assets'][0]['digest'] = 'sha256:' + '0' * 64
        with self.assertRaises(ValueError):select_update([item], '062')

    def test_foreign_host_and_filename_cannot_supply_installer(self):
        for url in ('http://github.com/unsafe.exe', 'https://evil.example/update.exe',
                    'https://github.com/other-owner/other-repo/update.exe'):
            item = release(); item['assets'][0]['browser_download_url'] = url
            with self.assertRaises(ValueError):select_update([item], '062')

    def test_incomplete_latest_build_does_not_silently_downgrade(self):
        newest = release('064'); newest['assets'] = []
        with self.assertRaises(ValueError):select_update([newest, release('063')], '062')

    def test_bounded_json_service_response(self):
        result = check_for_update('062', opener=lambda _: io.BytesIO(json.dumps([release()]).encode()))
        self.assertEqual(result.build, '063')
        with self.assertRaises(ValueError):check_for_update('062', opener=lambda _: io.BytesIO(b'x' * (2 * 1024 * 1024 + 1)))

    def test_network_error_is_reported(self):
        with self.assertRaises(OSError):check_for_update('062', opener=Mock(side_effect=OSError('offline')))


class DownloadTests(unittest.TestCase):
    def test_verified_download_published_only_after_complete(self):
        update = select_update([release()], '062')
        with tempfile.TemporaryDirectory() as directory:
            progress = Mock()
            path = download_update(update, directory, progress, opener=lambda _: io.BytesIO(DATA))
            self.assertEqual(path.read_bytes(), DATA)
            self.assertEqual(list(Path(directory).iterdir()), [path])
            progress.assert_called_with(len(DATA), len(DATA))

    def test_tampered_truncated_oversized_and_non_exe_downloads_removed(self):
        for data in (b'MZ' + b'X' * (len(DATA) - 2), DATA[:-1], DATA + b'X', b'XX' + DATA[2:]):
            with self.subTest(length=len(data)), tempfile.TemporaryDirectory() as directory:
                update = select_update([release()], '062')
                with self.assertRaises(ValueError):download_update(update, directory, opener=lambda _: io.BytesIO(data))
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_failed_download_preserves_existing_installer(self):
        update = select_update([release()], '062')
        with tempfile.TemporaryDirectory() as directory:
            previous = Path(directory) / update.filename
            previous.write_bytes(DATA)
            with self.assertRaises(OSError):download_update(update, directory, opener=Mock(side_effect=OSError('offline')))
            self.assertEqual(previous.read_bytes(), DATA)
            self.assertEqual(list(Path(directory).iterdir()), [previous])


class InstallTests(unittest.TestCase):
    def make_window(self, directory):
        window = UpdateWindow.__new__(UpdateWindow)
        window.busy = False; window.win = Mock(); window.app = Mock()
        window.update = select_update([release()], '062')
        window.installer = Path(directory) / window.update.filename
        window.installer.write_bytes(DATA)
        return window

    def test_declining_save_confirmation_leaves_session_running(self):
        with tempfile.TemporaryDirectory() as directory:
            window = self.make_window(directory)
            with patch('update_window.sys.platform', 'win32'), patch('update_window.messagebox.askyesno', return_value=False), patch('update_window.subprocess.Popen') as launch:
                window.install_update()
            launch.assert_not_called(); window.app.close.assert_not_called()

    def test_reverify_before_launch_then_close_session(self):
        with tempfile.TemporaryDirectory() as directory:
            window = self.make_window(directory)
            with patch('update_window.sys.platform', 'win32'), patch('update_window.messagebox.askyesno', return_value=True), patch('update_window.subprocess.Popen') as launch:
                window.install_update()
            launch.assert_called_once_with([str(window.installer)])
            window.app.close.assert_called_once_with()

    def test_changed_download_cannot_be_launched(self):
        with tempfile.TemporaryDirectory() as directory:
            window = self.make_window(directory); window.installer.write_bytes(b'corrupted')
            with patch('update_window.sys.platform', 'win32'), patch('update_window.messagebox.askyesno', return_value=True), patch('update_window.messagebox.showerror') as error, patch('update_window.subprocess.Popen') as launch:
                window.install_update()
            launch.assert_not_called(); window.app.close.assert_not_called(); error.assert_called_once()

    def test_failed_installer_launch_leaves_daw_running(self):
        with tempfile.TemporaryDirectory() as directory:
            window = self.make_window(directory)
            with patch('update_window.sys.platform', 'win32'), patch('update_window.messagebox.askyesno', return_value=True), patch('update_window.messagebox.showerror'), patch('update_window.subprocess.Popen', side_effect=OSError('cannot start')):
                window.install_update()
            window.app.close.assert_not_called()
