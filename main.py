import json
import csv
import sys
import zipfile
import os


def extract_header_value(headers, name):
    """
    Extracts the value of a header with the specified name from the headers list.
    Returns an empty string if the header is not found.
    """
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return ''


def read_har_and_export_csv(har_filename, csv_filename):
    """
    Reads a HAR JSON file and exports selected data to a CSV file.
    """
    with open(har_filename, 'r', encoding='utf-8') as har_file:
        har_data = json.load(har_file)

    entries = har_data['log']['entries']
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # Write the header row
        writer.writerow([
            'pageRef', 'startedDateTime', 'requestMethod', 'requestUrl',
            'requestHttpVersion', 'requestHeaderSize', 'requestBodySize',
            'responseStatus', 'responseContentSize', 'responseContentType',
            'responseContentLength', 'responseCacheControl', 'blocked',
            'dns', 'ssl', 'connect', 'send', 'wait', 'receive', 'time'
        ])

        # Write each entry
        for entry in entries:
            request = entry['request']
            response = entry['response']
            timings = entry['timings']
            responseHeaders = response.get('headers', [])

            writer.writerow([
                entry.get('pageref', ''),
                entry.get('startedDateTime', ''),
                request.get('method', ''),
                request.get('url', ''),
                request.get('httpVersion', ''),
                request.get('headersSize', ''),
                request.get('bodySize', ''),
                response.get('status', ''),
                response.get('content', {}).get('size', ''),
                extract_header_value(responseHeaders, 'content-type'),
                extract_header_value(responseHeaders, 'content-length'),
                extract_header_value(responseHeaders, 'cache-control'),
                timings.get('blocked', ''),
                timings.get('dns', ''),
                timings.get('ssl', ''),
                timings.get('connect', ''),
                timings.get('send', ''),
                timings.get('wait', ''),
                timings.get('receive', ''),
                entry.get('time', '')
            ])


def unzip_har(zip_filename):
    """
    Unzips a ZIP file and returns the path to the contained HAR file.
    Assumes there is only one HAR file in the ZIP archive.
    """
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        har_files = [f for f in zip_ref.namelist() if f.endswith('.har')]
        if not har_files:
            raise ValueError("No .har file found in the ZIP archive.")
        har_filename = har_files[0]  # Assuming only one HAR file is present
        zip_ref.extract(har_filename)
        return har_filename


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if file_path.lower().endswith('.zip'):
        # Process ZIP file
        try:
            har_filename = unzip_har(file_path)
            csv_filename = har_filename.rsplit('.', 1)[0] + '.csv'
            read_har_and_export_csv(har_filename, csv_filename)
            os.remove(har_filename)  # Clean up extracted HAR file
        except ValueError as e:
            print(e)
    elif file_path.lower().endswith('.har'):
        # Directly process HAR file
        csv_filename = file_path.rsplit('.', 1)[0] + '.csv'
        read_har_and_export_csv(file_path, csv_filename)
    else:
        print("Unsupported file format. Please provide a .har or .zip file containing a .har file.")
