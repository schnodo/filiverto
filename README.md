# filiverto
File Link Verifier for ToDoList

## About

filiverto checks XML task lists in Abstractspoon's ToDoList format for dangling file references. Those are caused by moving the task list to another directory or by moving or deleting the referenced files or folders. filiverto checks for "file links" and for links in the comments field. filiverto is written in Python.

## How it works
Currently, it does the following:

### Prepare
<ol>
  <li>If one command line argument is present, this is treated as the file path. Otherwise, users are presented with a file selection dialog, which lets them choose the task list to check.</li>
  <li>If the file path is invalid or the user cancels the selection, filiverto terminates.</li>
  <li>The working directory is set to the directory of the task list; that makes it easier to check relative links.</li>
  <li>An XML parser parses the ToDoList.</li><br>
</ol>

### Extract  
<ol>
  <li>All links and their respective parent's task IDs are extracted into a list.<li><br>  
  (The ID makes it easier to find the problematic tasks when cleaning up the task list afterwards.)</li>
  <li>First, FILEREFPATH elements are handled, then COMMENTS.</li>  
  <ul>
    <li>Every FILEREFPATH contains one link and nothing else, which makes extraction straightforward.</li>
    <li>For COMMENTS, checking against a few patterns is performed because potentially multiple links have to be separated from the surrounding text.</li>
  </ul>
  <li>One by one the links are cleaned up and checked.</li>

  <li>Any other kind of URL reference is ignored.</li>
  <li>If a file is not found, it is added to the list of missing references.</li>
</ol>

### Report
<ol>
  <li>After processing all entries, a messagebox informs the user about the result.</li>
  <li>To facilitate sorting by task ID or by file path, the report is stored in CSV format. (In case the report is opened with Excel, a few precautions are taken.) The report lies in same directory as the ToDoList.</li>
</ol>

## Limitations
- filiverto does not verify hyperlinks (http(s)://)
- the search patterns are incomplete and will not match all possible combinations of legal characters
