# ----------------------------------------------
# 6. v3_log_writer.py
# ----------------------------------------------
# Writes logs to a file.

class LogWriter:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path

    def write(self, log):
        if log:
            with open(self.log_file_path, 'a') as f:
                f.write(log + '\n')
