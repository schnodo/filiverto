# Check if files that are referenced by task list file links actually exist.
# If not, write the Task IDs and defective file links to a CSV file.
# Only tdl:// and file:// links are checked; so no validation of links to the 
# Internet is performed.

import os
from sys import exit
from sys import argv
import csv
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import urllib.parse
import re

# lxml is not part of the standard library.
# Install it from the command line with "pip install lxml"
from lxml import etree

# Format tdl:// links so that they can be used with file operations
def format_tdl_protocol(link):
    # Remove the protocol identifier
    link = link[6:]
    # Remove direct task id references for other task lists, such as tdl://test.tdl?1234
    id_pos = link.find("?")
    if id_pos != -1:
        link = link[:id_pos]
    return link

# Verify that a file exists; if it is missing, add it to the list of missing files
def check_and_add(id, link, missing_files):
    # clean up %20 characters as in tdl://todolist%20test.tdl
    link = urllib.parse.unquote(link)

    if os.path.isfile(link) == False and os.path.isdir(link) == False:
        missing_files.append({"id": id, "file": link})
        return True
    else:
        return False

# Gather defective links from the FILEREFPATH element
def process_FILEREFPATH(xml_tree):
    missing_files = []
    checked_links = 0
    refpaths = xml_tree.xpath("//FILEREFPATH")
    for refpath in refpaths:
        id = refpath.getparent().attrib['ID']
        link = refpath.text
        # Check tdl:// links
        if "tdl://" in link:
            link = format_tdl_protocol(link)
            if link.isnumeric():
                # Link to a task in the same ToDoList, nothing to do
                continue
            if check_and_add(id, link, missing_files):
                continue
        # All other protocols/hyperlinks are ignored
        if "//" not in link:
            check_and_add(id, link, missing_files)
    return missing_files, len(refpaths)

# Gather defective links from the COMMENTS element
def process_COMMENTS(xml_tree):
    # Check list of tdl:// links
    def process_tdls(proc_id, matches, missing_files):
        for match in matches:
            link = format_tdl_protocol(match[0])
            if len(link.strip()) == 0 or link.isnumeric():
                # Empty link or link to a task in the same ToDoList; nothing to do
                continue
            check_and_add(proc_id, link, missing_files)

    missing_files = []
    checked_links = 0
    refs = xml_tree.xpath("//COMMENTS")
    for ref in refs:
        id = ref.getparent().attrib['ID']    
        comments = ref.text

        # Check for tdl:// that includes spaces, marked by a "<" character
        re_tdl_spaces = r"<(tdl://([a-zA-Z]:)?[/\\.\w\s\-,()_]*)>"
        # Check for tdl:// in parentheses; In that case, the trailing parenthesis
        # has to be excluded from the file path
        re_tdl_parentheses = r"\((tdl://([a-zA-Z]:)?[^\s<>\*\"|?]*)\)"
        # Check for tdl:// without spaces, not embedded in brackes or parentheses
        re_tdl_no_spaces = r"(?<!\()(?<!<)(tdl://([a-zA-Z]:)?[^\s<>\*\"|?]*)"

        matches = []
        patterns = [re_tdl_spaces, re_tdl_parentheses, re_tdl_no_spaces]
        for pattern in patterns:
            matches += re.findall(pattern, comments)

        process_tdls(id, matches, missing_files)
        checked_links += len(matches)

        # Check for file:// that includes spaces, embedded in "<>" characters
        re_file_spaces = r"<file:/{2,3}(([a-zA-Z]:)?[/\\.\w\s\-,()_]*)>"
        # Check for file:// in parentheses; In that case, the trailing parenthesis
        # has to be excluded from the file path
        re_file_parentheses = r"\(\s?file:/{2,3}(([a-zA-Z]:)?([^\s<>]|[/\\.\w\-,()_])*)"
        # Check for file:// without spaces, not embedded in brackes or parentheses
        re_file_no_spaces = r"(?<!\(\s)(?<!\()(?<!<)file:/{2,3}(([a-zA-Z]:)?([^\s<>]|[/\\.\w\-,()_])*)"

        matches = []
        patterns = [re_file_spaces, re_file_parentheses, re_file_no_spaces]
        for pattern in patterns:
            matches += re.findall(pattern, comments)

        for match in matches:
            check_and_add(id, match[0], missing_files)
        checked_links += len(matches)

    return missing_files, checked_links

# Save the missing files report as "<<ToDoList name>>_missing_files.csv"
def save_csv_report(file_path, missing_files):
    # newline='' is necessary to prevent Excel from showing empty lines.
    # utf-8-sig needs to be chosen as encoding because Excel expects a BOM, 
    # otherwise umlauts are not properly displayed.
    with open(file_path[0:len(file_path) - 4] + "_missing_files.csv", 'w', newline='',encoding='utf-8-sig') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # CSV header row
        csvwriter.writerow(["Task ID", "File Link"])

        for entry in missing_files:
            csvwriter.writerow([entry['id'], entry['file']])    

# Execution of the main routine starts here
tk_root = tk.Tk()
tk_root.withdraw()

# Try to load the ToDoList icon for the dialogs
# It is assumed to be in the same directory as the script
icon_path = ""
icon_path = os.path.dirname(__file__) + '\ToDoList_2004.ico'
if os.path.isfile(icon_path):
    tk_root.iconbitmap(icon_path)

# Get the file name for the task list from an argument or
# by means of a file open dialog
if len(argv) > 2:
    messagebox.showinfo(title="Too many arguments", 
    message="Please provide \n* no argument or \n* the file name of the ToDoList as the only argument.")
    exit(1)
elif len(argv) > 1:
    file_path = argv[1]
else:
    file_path = filedialog.askopenfilename(initialdir=".", title = "Choose ToDoList for verifying file links", filetypes=[("Abstractspoon ToDoList", ".tdl")])

if os.path.isfile(file_path) == False:
    if len(argv) > 1:
        messagebox.showinfo(title="File not found", 
        message = "The file \n" + file_path + "\ncould not be found.")
    exit(1)

# Set working directory to make sure that relative file links will be evaluated correctly.
if os.path.dirname(file_path):
    os.chdir(os.path.dirname(file_path))

xml_parser = etree.XMLParser(remove_blank_text=True)
xml_tree = etree.parse(file_path, xml_parser)

# Gather all dangling file references and their task IDs
missing_files = []
num_links = 0
missing_filerefpath_files, num_filerefpath_links = process_FILEREFPATH(xml_tree)
missing_comments_files, num_comments_links = process_COMMENTS(xml_tree)
missing_files = missing_filerefpath_files + missing_comments_files
num_links = num_filerefpath_links + num_comments_links

if not missing_files:
    messagebox.showinfo(title="Process completed", message = str(num_links) + " links checked.\n" + "Congratulations! There are no dangling file references.")
    exit(0)

if len(missing_files) > 1:
    msg_text = " defective file links were found."
else:
    msg_text = " defective file link was found."

messagebox.showinfo(title="Process completed", message = str(num_links) + " links checked.\n" + str(len(missing_files)) + msg_text)

save_csv_report(file_path, missing_files)    
exit(0)