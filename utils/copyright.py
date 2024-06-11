import os
import sys

DEFAULT_COPYRIGHT_TEXT = """
Author: Tanmay Rajore\n
Copyright:\n
Copyright (c) 2024 Microsoft Research\n
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
def add_copyright_to_files(directory, copyright_text):
    # Get a list of all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    for file in files:
        filename = os.path.join(directory, file)
        try:
            # Open the file in read mode
            with open(filename, 'r') as f:
                file_content = f.read()

            # Determine the file type based on the file extension
            file_extension = os.path.splitext(filename)[1]
            print(filename)
            print(file_extension)
            if file_extension in ['.py']:
                comment_prefix = '# '
            elif file_extension in ['.js']:
                comment_prefix = '// '
            elif file_extension in ['.c', '.cpp', '.h', '.hpp', '.cu', '.cuh']:
                comment_prefix = '// '
            else:
                comment_prefix = '/*'


            # Open the file in write mode
            with open(filename, 'w') as f:
                # Write the copyright text as a comment if provided
                if copyright_text:
                    for line in DEFAULT_COPYRIGHT_TEXT.splitlines():
                        print(line)
                        f.write(comment_prefix + line + '\n')
                # Write an empty line after the copyright text
                f.write('\n')
                # Write the original content
                f.write(file_content)
            print(f"Copyright text added to '{filename}' successfully.")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_copyright.py <directory_path> [copyright_text]")
        sys.exit(1)

    directory = sys.argv[1]

    if not os.path.isdir(directory):
        print("Error: Directory not found.")
        sys.exit(1)

    copyright_text = None
    if len(sys.argv) == 3:
        copyright_text = sys.argv[2]

    add_copyright_to_files(directory, copyright_text)