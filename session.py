import hashlib
import os

from requests import session


class session():
    @staticmethod
    def generateCsrf():
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        session['state'] = state