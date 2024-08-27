# GeoExplorer Client

This is the client component of the GeoExplorer project, designed to send requests to GeoServer instances and test for potential vulnerabilities.

## Requirements

- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`):
  - requests
  - argparse
  - urllib3

## Usage

Run the script with the following command:

`python main.py -u <target_url_or_file> -t <threads> -c <catcher_url>`

Arguments:
- `-u`: Target URL or file containing newline-delimited URLs (required)
- `-t`: Number of threads (default: 100)
- `-c`: Catcher URL (default: http://127.0.0.1:8000/log) (point this at the included server)

## How it works

The script performs the following actions:

1. Parses command-line arguments
2. Processes target URLs (either a single URL or multiple URLs from a file)
3. Uses the `ListStoredQueries` request on WFS to automagiclly find a valid feature type.
4. Sends requests to the specified GeoServer instances with a wget payload towards the defined catcher.

For more details, see the `main.py` file.