## Current

* Most of the focus has been on web_connectivity tests. Parsing the DNS consistency files might not be as robust or error
free as the web_connectivity measurements

* Note the way data is being populated into the database; if a certain data
in the measurement files is not found, it is replaced with the string 'error'. This might
require some revisions especially with the dns_consistency tests. 

* I assume more testing would be required for the body search feature as it was only recently added and testing on the 
back-end was not sufficient

### Problems to fix:
* The deployment; for instance, it currently seems like ansible is not giving the proper database access to the users.
Additionally, when handling large/long requests, apache errors out (as discussed, it may be a RAM issue).

### Errors:
* **Status**: Temp Fix

  **Error**: ValueError: A string literal cannot contain NUL (0x00) characters.

  **When**: Headers search for WireFilter from 2018-06-01 to 2018-06-02 in KR
  
  **Temp Fix**: Added ValueError exception. Seems like a problem with Postgres not allowing NUL (0x00) characters. Tell
  sqlalchemy to rollback session once exception is raised
  
