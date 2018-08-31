## Dev Notes

### Notes on design
* In the process of downloading files, the app is currently downloading files into the UPLOAD directory 
(macro defined in config file), then serving it to the browser.
The original file in the UPLOAD directory is deleted. This is done so users can define the directory path through their 
browser; however this seems very wasteful

* Currently, the API resources for downloading tables are tailored towards the web UI. It follows the above cycle of 
downloading the file, serving it to the browser, and deleting the original file. To work around this, an API parameter 
called api_download was added to the /webconn and /dns_consistency endpoints for downloading specific files. If
the parameter is set to 'true', the program will simply download the csv in the user's home directory