# Web Application In Python + FastAPI

## Generates and stores 6 character short URLs for given long URLs (in sqlite)

### Exposes a simple Web UI on /

### Two GET APIs:
/api/urls : Lists all available URLs
/{short_code} : Lists the long url for the given code

### POST API:
/shorten: accepts original_url and returns short_url

### DELETE API:
/api/urls/{short_code}: Deletes the given short code and corresponding URL

**Jinja2Templates for UI integration**

** Checks whether URL is reachable **

** Displays created at time, recently saved URLs and delete option on UI **

** Have switch to toggle dark theme and light theme **

Supports upto 500 URLs
