# OONI-pipeline

version number: 0.0.1
author: Steve Kim

## Overview

OONI-pipeline stores OONI measurement data that fits the user's specifications. Given an input, the application stores
data extracted from the reports for use. Additional features include searching response bodies 
and headers in web_connectivity reports, where users can specify the data they want.

## Select, Store, and Download

You can select what data to store with the following specifications:

* Country Code
* Date
* ASN #
* URLs
* Name of test

The data is stored in a table containing selected information from the report files. Once the
table is made, its basic information such as its name, date of creation and description
is stored in a Meta Table which can later be viewed for reference. A description of
the table can also be edited post creation through a PUSH request.

Once the storing process is complete, you can download specific tables that each contain different information
about a data set. 

## Notes
Read doc file for dev notes.


## License

This is licensed under [the BSD 3-Clause License](LICENSE).
