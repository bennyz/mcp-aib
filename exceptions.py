"""
MIT License

Copyright Red Hat.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""AIB Exceptions module"""


class AIBException(Exception):
    pass


class InvalidOption(AIBException):
    def __init__(self, option, value):
        self.option = option
        self.value = value

    def __str__(self):
        return (
            f"Invalid value passed to {self.option}: '{self.value}': "
            "should be key=value"
        )


class MissingSection(AIBException):
    def __init__(self, section):
        self.section = section

    def __str__(self):
        return f"No {self.section} section in manifest"


class DefineFileError(AIBException):
    pass


class ManifestParseError(AIBException):
    def __init__(self, manifest_path):
        self.manifest = manifest_path

    def __str__(self):
        return f"Error parsing {self.manifest}"


class SimpleManifestParseError(AIBException):
    def __init__(self, manifest_path, errors):
        self.manifest = manifest_path
        self.errors = errors

    def __str__(self):
        return f"Error parsing {self.manifest}:\n " + "\n ".join(
            e.message for e in self.errors
        )


class UnsupportedExport(AIBException):
    def __init__(self, export):
        self.export = export

    def __str__(self):
        return f"Unsupported export '{self.export}'"


class InvalidMountSize(AIBException):
    def __init__(self, mountpoint):
        self.mountpoint = mountpoint

    def __str__(self):
        return f"{self.mountpoint} can't be larger than image"


class InvalidMountRelSize(AIBException):
    def __init__(self, mountpoint):
        self.mountpoint = mountpoint

    def __str__(self):
        return f"Invalid relative size for {self.mountpoint}, must be between 0 and 1"
