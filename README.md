# LIBRARIAN

`librarian.py` is a tool for organizing important datasets in a
data engagement.  Anything that is obtained from an external source,
or that is shipped to an external source, should be tracked using
`librarian.py`.

Any engagement with an external data partner involves keeping data
safe, documenting data effectively, tracking data versions, and
sharing data with internal and external partners.  Doing this in a
plain old filesystem will drive you crazy.  Librarian helps you not go
crazy.

Librarian offers three basic services:
* Fast and reliable copying of files to/from AWS storage
* Accompanying file data with project, version, and comment metadata
* Encouraging good practices by prompting the user to include certain
  special comments and metadata when performing data ingest or
  outgest.

# Commands

Librarian supports the following commands:
* `ls` lists all the projects under management
* `examine` provides details about a project, a Librarian directory,
  or a specific version of a Librarian directory
* `cp` copies data from a Librarian directory to a local filesystem
  directory.
* `createproj` creates a brand-new Librarian project  
* `ingest` creates a brand-new ingest directory under a Librarian
  project.  Or, if the directory already exists, creates a new version
  of the previously-known directory
* `outgest` creates a brand-new outgest directory under a Librarian
  project  Or, if the directory already exists, creates a new version
  of the previously-known directory


# Walkthrough

Here are a few examples of how to use Librarian.

You can use Librarian to view the data status of current projects:

```
$ librarian.py --ls

genomics	feng	created 2015-04-02 05:54:26.511870	updated 2015-04-02 05:54:26.511877
toshiba	mjc	created 2015-04-02 05:54:37.792339	updated 2015-04-02 05:54:37.792347

$ librarian.py --examine toshiba --comments
name: toshiba
owner: mjc
created: 2015-04-02 05:54:37.792339
updated: 2015-04-02 05:54:37.792347
comments: Toshiba guys are great

There are 0 ingested directories

There are 0 outgested directories

  
$ librarian.py --createproj memex mjc
Please describe the project
$ This is the DARPA Memex project
Created project memex


$ librarian.py --examine memex --comments
name: memex
owner: mjc
created: 2015-04-02 05:39:45.057358
updated: 2015-04-02 05:39:45.057366
comments: This is the DARPA Memex project

There are 0 ingested directories

There are 0 outgested directories

$ librarian.py --ingest memex data-drop-1 ./prepDirForMemexDataDrop
Ingesting data for project memex under directory data-drop-1
Processing 2 files from ./prepDirForMemexDataDrop
How was this data obtained?
[0]  Data was obtained directly from data partner.
[1]  Data is result of SQL query against data partner database.
[2]  Data is result of running processing program over a raw partner file.
[3]  Data comes from some other source
$ 1
Describe how data was obtained from partner (e.g., URL or scp path)
$ We grabbed it from the IST standard Memex MySQL database, described in the Memex Wiki.
Total bytes transferred: 191739 total size: 191739


$ librarian.py --examine memex
name: memex
owner: mjc
created: 2015-04-02 05:39:45.057358
updated: 2015-04-02 05:39:45.057366
comments: This is the DARPA Memex project

There are 1 ingested directories
data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:01:39.727166	665cf577a85b4bafb2892e9e69970d82

$ librarian.py --examine memex --comments
name: memex
owner: mjc
created: 2015-04-02 05:39:45.057358
updated: 2015-04-02 05:39:45.057366
comments: This is the DARPA Memex project

There are 1 ingested directories
data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:01:39.727166	665cf577a85b4bafb2892e9e69970d82
(comments: Data is result of SQL query against data partner database.
We grabbed it from the IST standard Memex MySQL database, described in the Memex Wiki.)



There are 0 outgested directories


$ librarian.py --examine memex:data-drop-1
name: memex
owner: mjc
created: 2015-04-02 05:39:45.057358
updated: 2015-04-02 05:39:45.057366
data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:01:39.727166	665cf577a85b4bafb2892e9e69970d82

	disturbing.txt	191739	0fffc3a43e0bebff718456f25394c0b9
	terrifying.txt	119767	2d3b2ac7becee4ec477e4df512482d71


$ mv forgottenHorribleMemexFile.txt prepDirForMemexDataDrop/

$ librarian.py --ingest memex data-drop-1 ./prepDirForMemexDataDrop
Ingesting data for project memex under directory data-drop-1
Processing 3 files from ./prepDirForMemexDataDrop
How was this data obtained?
[0]  Data was obtained directly from data partner.
[1]  Data is result of SQL query against data partner database.
[2]  Data is result of running processing program over a raw partner file.
[3]  Data comes from some other source
$ 1
Describe how data was obtained from partner (e.g., URL or scp path)
$ This comes from the IST SQL database from the Memex wiki.  This update includes a file I initially forgot to grab 


$ librarian.py --examine memex:data-drop-1
name: memex
owner: mjc
created: 2015-04-02 05:39:45.057358
updated: 2015-04-02 05:39:45.057366
data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:06:58.596147	c368c90c933641a0a4c5fe06cf987d89

	disturbing.txt	191739	0fffc3a43e0bebff718456f25394c0b9
	forgottenHorribleMemexFile.txt	110371	26595cbeef505b27fbbe78a767285e5a
	terrifying.txt	119767	2d3b2ac7becee4ec477e4df512482d71

$ librarian.py --examine memex:data-drop-1:all
name: memex
owner: mjc
created: 2015-04-02 05:39:45.057358
updated: 2015-04-02 05:39:45.057366
data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:01:39.727166	665cf577a85b4bafb2892e9e69970d82
	disturbing.txt	191739	0fffc3a43e0bebff718456f25394c0b9
	terrifying.txt	119767	2d3b2ac7becee4ec477e4df512482d71

data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:06:58.596147	c368c90c933641a0a4c5fe06cf987d89
	disturbing.txt	191739	0fffc3a43e0bebff718456f25394c0b9
	forgottenHorribleMemexFile.txt	110371	26595cbeef505b27fbbe78a767285e5a
	terrifying.txt	119767	2d3b2ac7becee4ec477e4df512482d71


$ librarian.py --examine memex:data-drop-1:all --comments
name: memex
owner: mjc
created: 2015-04-02 05:39:45.057358
updated: 2015-04-02 05:39:45.057366
comments: This is the DARPA Memex project

data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:01:39.727166	665cf577a85b4bafb2892e9e69970d82
comments: Data is result of SQL query against data partner database.
We grabbed it from the IST standard Memex MySQL database, described in the Memex Wiki.

	disturbing.txt	191739	0fffc3a43e0bebff718456f25394c0b9
	terrifying.txt	119767	2d3b2ac7becee4ec477e4df512482d71

data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:06:58.596147	c368c90c933641a0a4c5fe06cf987d89
comments: Data is result of SQL query against data partner database.
This comes from the IST SQL database from the Memex wiki.  This update includes a file I initially forgot to grab

	disturbing.txt	191739	0fffc3a43e0bebff718456f25394c0b9
	forgottenHorribleMemexFile.txt	110371	26595cbeef505b27fbbe78a767285e5a
	terrifying.txt	119767	2d3b2ac7becee4ec477e4df512482d71


$ librarian.py --cp memex:data-drop-1 ./localDataShipmentDir
Copying data from following Librarian directory:
data-drop-1	ingest	2015-04-02 06:01:39.727159	2015-04-02 06:06:58.596147	c368c90c933641a0a4c5fe06cf987d89
Copying disturbing.txt from Librarian to ./localDataShipmentDir
Total bytes transferred: 191739 total size: 191739

Copying forgottenHorribleMemexFile.txt from Librarian to ./localDataShipmentDir
Total bytes transferred: 110371 total size: 110371

Copying terrifying.txt from Librarian to ./localDataShipmentDir
Total bytes transferred: 119767 total size: 119767
```







  
  
