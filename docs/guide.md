## Guides

### Adding additional tests to study (whatsapp, facebook_messenger, etc)
1. Map out the different models to be used for parsing and storing specific data from the test's measurement files
(including their relationships)

2. Go to store.py which is the back-end for the select/store endpoint. After the declarations of the API parameters,
add the test name to validate user inputs. You will notice that the query and filter process is the same for all the
tests until the need to populate the test's specific models. Whether the user provides a URL to filter by
(url is not None) or not (url is None), you will need to populate the test's models using table_pop's functions.

3. Go to table_pop.py and create a new function that follows the naming convention: {test-name}_pop(). The function will 
need to take all the models associated with the test that requires population from the test's measurement files. Here 
you have two options. Create a function under the OoniDataParser class that extensively parses the wanted data into the 
'useful_list' so that in table_pop.py, you will only need to access the elements of the list to populate the models
(this method was used for the dns_consistency test), or do all the parsing in table_pop.py (web_connectivity way).

4. The next step would be to add API endpoints that download the tables under the resources directory. Follow webconn.py
or dns_consistency.py for a rough template

5. Add these endpoints under the controllers directory in api.py to make the endpoints accessible

6. Connect to web UI if you wish!