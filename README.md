# filiverto
File Link Verifier for AbstractSpoon's ToDoList

## About

filiverto checks XML task lists in [AbstractSpoon's ToDoList](https://github.com/abstractspoon/ToDoList_8.1) format for dangling file references. Those are most commonly caused by 
  - moving the task list to another directory or
  - by moving/deleting the referenced files or folders.
  
filiverto checks for "file links" and for links in the comments field.

![Screenshot of ToDoList preferences with filiverto set up as user-defined tool](https://github.com/schnodo/filiverto/blob/screenshots/filiverto_user-defined-tool.jpg)

filiverto can be used as user-defined tool in ToDoList, making it possible to verify the currently active task list.

filiverto is written in Python.

## Setup and execution
Assuming that Python is already installed on your system, simply copy the files contained in the repository into a directory and run <code>filiverto.pyw</code>.<br/>

If you haven't installed Python yet, you can download the most current version from the [Python website](https://www.python.org/downloads/). filiverto was tested with Python 3.10.

filiverto uses the xlml package, which is not part of the standard library. If you don't have it installed already, add it by executing this command in a console:<br/>
<code>pip install lxml</code>

## How it works
Currently, it does the following:

### Prepare
<ol>
  <li>If one argument is passed to filiverto, this is treated as the file path. Otherwise, users are presented with a file selection dialog, which lets them choose the task list to check.</li>
  <li>If the file path is invalid or the user cancels the selection, filiverto terminates.</li>
  <li>The working directory is set to the directory of the task list; that makes it easier to check relative links.</li>
  <li>An XML parser parses the task list.</li><br>
</ol>

### Extract and Verify
<ol>
  <li>All links and their respective parent's task <code>IDs</code> are extracted into a list. (The <code>ID</code> makes it easier to find the problematic tasks when cleaning up the task list afterwards.) First, <code>FILEREFPATH</code> elements are handled, then <code>COMMENTS</code>.</li>
  <ul>
    <li>Every <code>FILEREFPATH</code> contains one link and nothing else, which makes extraction straightforward.</li>
    <li>For <code>COMMENTS</code>, matching against a few patterns is necessary because a comment field might contain multiple links, which have to be separated from the surrounding text.</li>
  </ul>
  <li>One by one the links are cleaned up and checked.</li>
  <ol>
    <li><code>tdl://</code> references get special treatment</li>
      <ul>
        <li>Direct links within the task list (<code>tdl://1234</code>) are ignored.</li>
        <li>For links to other task lists (<code>tdl://test.tdl?1234</code>), potential task references (<code>?1234</code>) are removed.</li>
      </ul>
    <li>Escaped characters (<code>tdl://todolist%20test.tdl</code>) are unescaped.</li>
    <li>Any kind of URL reference besides <code>tdl://</code> and <code>file://</code> is ignored.</li>    
    <li>The protocol identifier (<code>tdl://</code> and <code>file://</code>) is removed.</li>
    <li>What remains, hopefully is a file name and its existence is verified.</li>
    <li>If a file is not found, it is added to the list of missing references.</li>
  </ol>    
</ol>

### Report
<ol>
  <li>After processing all entries, a messagebox informs the user about the number of processed entries and the number of defective file links.</li>
  <li>To facilitate sorting by task ID or by file path, the report is stored in CSV format. (In case the report is opened with Excel, a few precautions are taken.) The report lies in same directory as the task list.</li>
</ol>

## Limitations
<ul>
  <li>filiverto does not verify other kinds of hyperlinks, such as those that typically link to a website on the Internet (<code>http(s)://</code>)</li>
  <li>The search patterns for the <code>COMMENTS</code> element are not fully reliable. They will in some cases</li>
  <ul>
    <li>not match all possible combinations of legal characters or</li>
    <li>match more characters than desired, for example when providing arguments to an executable: <code>todolist.exe -cmd 32828</code><br/>
    Unfortunately that's a semantic problem because this also represents a legal file name as you can see in the screenshot. Maybe next year I'll program the AI to keep them apart. 😉</li>
  </ul>
</ul>

![Example of a legal Windows file name that does not look legal](https://github.com/schnodo/filiverto/blob/screenshots/unexpectedly_legal_file_name.jpg)

## Next steps
- Figure out if it is possible to make filiverto usable without having to install packages via the command line.
- Make filiverto installable through pip.
- Create more test cases
