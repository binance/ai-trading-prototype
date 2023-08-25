import time


class FileOperator:
    """
    Class for File operations
    """

    def __init__(self, file_name: str, mode: str):
        """
        Initialize the FileOperator class with file name and mode
        """
        self.file_name = file_name
        self.file = open(file_name, mode)

    def follow_line(self, wait_time=1):
        """
        This method is used to follow a file like "tail -f file_name", i.e:
            - follows the file and yields line if there is any new line;
            - if not, it waits for `wait_time` (default: 1 second) and checks again;
        """

        while True:
            line = self.file.readline().strip()
            if not line:
                time.sleep(wait_time)
                continue
            yield line

    def write_line(self, line: str):
        """
        This method is used to write a line to file
        """
        self.file.write(line)
        self.file.flush()

    def close(self):
        """
        Close the file
        """
        self.file.close()
