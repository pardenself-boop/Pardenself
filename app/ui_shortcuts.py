"""Keep workstation shortcuts out of text and numeric editors."""

EDITABLE_CLASSES = {'Entry', 'TEntry', 'Text', 'Spinbox', 'TSpinbox', 'TCombobox'}


def dispatch_shortcut(event, action):
    if event.widget.winfo_class() in EDITABLE_CLASSES:
        return None
    action()
    return 'break'
