import sys
import unittest
from pathlib import Path
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from toolboxx import App
import launch_reference

class CustomerLaunchTests(unittest.TestCase):
    def test_launch_opens_one_workspace_and_closes_app_with_it(self):
        root=Mock();app=Mock();scheduled=[]
        root.after.side_effect=lambda delay,callback:scheduled.append(callback)
        root.mainloop.side_effect=lambda:scheduled[0]()
        with patch('launch_reference.tk.Tk',return_value=root),patch('launch_reference.App',return_value=app),patch.object(sys,'argv',['toolboxx']):launch_reference.main()
        app.open_cookup.assert_called_once();root.withdraw.assert_called_once()
        app.cookup_window.win.protocol.assert_called_once_with('WM_DELETE_WINDOW',app.close)
        app.cookup_window.win.bind.assert_not_called()
    def test_underlying_workstation_can_still_be_opened(self):
        app=App.__new__(App);app.root=Mock();app.show_workstation()
        app.root.deiconify.assert_called_once();app.root.lift.assert_called_once()
