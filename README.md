# filiverto
File Link Verifier for Abstractspoon's ToDoList

## About

filiverto checks XML task lists in [Abstractspoon's ToDoList](https://github.com/abstractspoon/ToDoList_8.1) format for dangling file references. Those are caused by moving the task list to another directory or by moving or deleting the referenced files or folders. filiverto checks for "file links" and for links in the comments field. filiverto is written in Python.

## How it works
Currently, it does the following:

### Prepare
<ol>
  <li>If one argument is passed to filiverto, this is treated as the file path. Otherwise, users are presented with a file selection dialog, which lets them choose the task list to check.</li>
  <li>If the file path is invalid or the user cancels the selection, filiverto terminates.</li>
  <li>The working directory is set to the directory of the task list; that makes it easier to check relative links.</li>
  <li>An XML parser parses the ToDoList.</li><br>
</ol>

### Extract  
<ol>
  <li>All links and their respective parent's task <code>IDs</code> are extracted into a list. (The <code>ID</code> makes it easier to find the problematic tasks when cleaning up the task list afterwards.) First, <code>FILEREFPATH</code> elements are handled, then <code>COMMENTS</code>.</li>
  <ul>
    <li>Every <code>FILEREFPATH</code> contains one link and nothing else, which makes extraction straightforward.</li>
    <li>For <code>COMMENTS</code>, matching against a few patterns is necessary because a comment field might contain multiple links, which have to be separated from the surrounding text.</li>
  </ul>
  <li>One by one the links are cleaned up and checked.</li>
  <ul>
    <li>"tdl://" references get special treatment</li>
      <ul>
        <li>Direct links within the ToDoList (<code>tdl://1234</code>) are ignored.</li>
        <li>For links to other ToDoLists (<code>tdl://test.tdl?1234</code>), potential task references (<code>?1234</code>) are removed.</li>
      </ul>
    <li>Escaped characters (tdl://todolist%20test.tdl) are unescaped.</li>
    <li>Any kind of URL reference besides <code>tdl://</code> and <code>file://</code> is ignored.</li>    
    <li>The protocol identifier (<code>tdl://</code> and <code>file://</code>) is removed.</li>
    <li>What remains, hopefully is a file name and its existence is verified.</li>
    <li>If a file is not found, it is added to the list of missing references.</li>
  </ul>    
</ol>

### Report
<ol>
  <li>After processing all entries, a messagebox informs the user about the number of processed entries and the number of defective file links.</li>
  <li>To facilitate sorting by task ID or by file path, the report is stored in CSV format. (In case the report is opened with Excel, a few precautions are taken.) The report lies in same directory as the ToDoList.</li>
</ol>

## Limitations
- filiverto does not verify hyperlinks (<code>http(s)://</code>)
- The search patterns for the COMMENTS element are currently incomplete and will not match all possible combinations of legal characters.
