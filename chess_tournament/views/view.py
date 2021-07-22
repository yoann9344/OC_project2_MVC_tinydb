from rich.layout import Layout


class LayoutView():
    def __init__(self):
        layout = Layout()
        self.layout = layout

        # Divide the 'screen' in to three parts
        layout.split(
            Layout(name='header', size=3),
            Layout(ratio=1, name='main'),
            Layout(size=10, name='footer'),
        )
        # Divide the 'main' layout in to 'side' and 'body'
        layout['main'].split_row(
            Layout(name='side'),
            Layout(name='body', ratio=2),
        )
        # Divide the 'side' layout in to two
        layout['side'].split(Layout(name='info'), Layout(name='dialog'))

        self.header = layout['header']
        main = layout['main']
        self.footer = layout['footer']

        side = main['side']
        self.body = main['body']

        self.info = side['info']
        self.dialog = side['dialog']

        self.line = 'PLOP'
