class NoGoogleDriveTokenFoundException(Exception):
    def __init__(self, *args):
        super().__init__('No Google Drive token file found')
