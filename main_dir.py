import json
import csv
import os
import sys


def extract_header_value(headers, name):
    """
    Extracts the value of a header with the specified name from the headers list.
    Returns an empty string if the header is not found.
    """
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return ''


def read_har_and_export_csv(directory_path, csv_filename):
    all_entries = []  # Step 1: Initialize the list to collect entries

    for filename in os.listdir(directory_path):
        if filename.endswith('.har'):
            har_path = os.path.join(directory_path, filename)
            with open(har_path, 'r', encoding='utf-8') as har_file:
                har_data = json.load(har_file)

            entries = har_data['log']['entries']
            for entry in entries:
                request = entry['request']
                response = entry['response']
                timings = entry['timings']
                responseHeaders = response.get('headers', [])
                responseContent = response.get('content', {}).get('size', 0)  # Default to 0 if 'size' is not found
                contentLengthHeader = extract_header_value(responseHeaders, 'content-length')
                contentLength = int(contentLengthHeader) if contentLengthHeader.isdigit() else 0
                transfer_size = response.get('_transferSize', 0)
                responseSize = responseContent + contentLength + transfer_size
                if responseSize == 0:
                    responseSize=transfer_size
                totalTime = entry.get('time', '')
                responseRate = responseSize / totalTime if totalTime > 0 else 0
                error = response.get('_error', '')

                # Add filename to the entry's data
                entry_data = [
                    filename,  # Include the file name in each entry
                    entry.get('startedDateTime', ''),
                    entry.get('connection', ''),
                    entry.get('_priority', ''),
                    request.get('method', ''),
                    request.get('url', ''),
                    request.get('httpVersion', ''),
                    response.get('status', ''),
                    error,
                    responseSize,
                    totalTime,
                    responseRate,
                    timings.get('blocked', ''),
                    timings.get('dns', ''),
                    timings.get('ssl', ''),
                    timings.get('connect', ''),
                    timings.get('send', ''),
                    timings.get('wait', ''),
                    timings.get('receive', ''),
                    timings.get('_blocked_queueing', ''),
                    timings.get('_blocked_proxy', '')
                ]
                all_entries.append(entry_data)

    # Step 3: Sort all_entries by 'startedDateTime' (which is at index 3 in each entry_data)
    all_entries.sort(key=lambda x: x[1])

    # Step 4: Write the sorted entries to the CSV file
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            'tab', 'startedDateTime', 'connection', 'priority', 'requestMethod', 'requestUrl',
            'requestHttpVersion', 'responseStatus', 'error', 'responseSize',
            'totalTime', 'responseRate (kb/s)', 'blocked',
            'dns', 'ssl', 'connect', 'send', 'wait', 'receive', 'blocked_queueing',
            'blocked_proxy'
        ])

        for entry_data in all_entries:
            writer.writerow(entry_data)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]
    if not os.path.isdir(directory_path):
        print(f"The provided path '{directory_path}' is not a directory.")
        sys.exit(1)

    directory_name = os.path.basename(os.path.normpath(directory_path))
    csv_filename = f"{directory_name}.csv"
    read_har_and_export_csv(directory_path, csv_filename)
    print(f"Data from HAR files in '{directory_path}' has been successfully exported to '{csv_filename}'.")
