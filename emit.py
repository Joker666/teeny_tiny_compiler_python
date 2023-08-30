# Emitter object keeps track of the generated code and outputs it.
class Emitter:
    def __init__(self, full_path):
        self.fullPath = full_path
        self.header = ""
        self.code = ""

    def emit(self, code):
        self.code += code

    def emit_line(self, code):
        self.code += code + "\n"

    def header_line(self, code):
        self.header += code + "\n"

    def write_file(self):
        with open(self.fullPath, "w") as outputFile:
            outputFile.write(self.header + self.code)
