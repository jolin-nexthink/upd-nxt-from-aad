"""Configuration settings for console app using device flow authentication
"""

# These settings are for the Microsoft Graph API Call
RESOURCE = "https://graph.microsoft.com"  # Add the resource you want the access token for
TENANT = "" # Your Tenant GUID or unique literal identifier
AUTHORITY_HOST_URL = "https://login.microsoftonline.com"
AUTHORITY_URL = AUTHORITY_HOST_URL + '/' + TENANT
CLIENT_ID = ""  # copy the Application ID of your app from your Azure portal
CLIENT_SECRET = ""  # copy the value of key you generated when setting up the application
API_VERSION = 'v1.0' # The Version of the MS Graph API to use in the REST calls
MAX_PAGES = 9999 # You can limit the max number of pages of users that are returned with this value
MAX_ROWS = '&$top=999' # You can control the size of a page of returned users with this value
FILTER = '' # specify any OData expressions here to further filter the users returned

# This is the list of fields to retrieve from the User
AAD_USER_FIELDS = [
    'id',
    'userPrincipalName',
    'displayName',
    'givenName',
    'surname',
    'mail'
]

# This code can be removed after configuring CLIENT_ID and CLIENT_SECRET above.
if 'ENTER_YOUR' in CLIENT_ID:
    print('ERROR: config.py does not contain valid CLIENT_ID.')
    import sys
    sys.exit(1)

# Utility function for determining elapsed time
# Inputs are from calls to time.time()
def timer(start, end):
    sec_elapsed = end - start
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.

    if h > 0:
        return "{} h {:>02} min {:>05.2f} sec".format(h, m, s)
    elif m > 0:
        return "{:>02} min {:>05.2f} sec".format(m, s)
    else:
        return "{:>05.2f} sec".format(s)

