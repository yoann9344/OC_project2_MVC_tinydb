import abc


class EditablePlugin(abc.ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editable_callback = None
        self.editable_activated = False

    def activate_edition(self, callback, multiline=False):
        self.editable_callback = callback
        self.editable_activated = True
        if multiline:
            self.page.loop.start_edition_mode(self.multine_editor)
        else:
            self.page.loop.start_edition_mode(self.single_editor)
        # self.page.loop.kb.desactivate()

    def desactivate_edition(self):
        self.page.loop.stop_edition_mode()
        self.editable_activated = False
        # self.page.loop.kb.activate()

    def multine_editor(self, buffer, last_entries, desactivated=False):
        self.editable_callback(buffer, last_entries, desactivated)

    def single_editor(self, buffer, last_entries, desactivated=False):
        if self.editable_callback is None:
            return
        if '\n' in last_entries:
            last_entries = last_entries.split('\n')[0]
            buffer = buffer.split('\n')[0]
            self.desactivate_edition()
        self.editable_callback(
            buffer,
            last_entries,
            desactivated=not self.editable_activated,
        )
