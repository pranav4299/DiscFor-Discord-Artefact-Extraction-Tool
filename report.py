# List of standard library imports
import json
import gzip
from csv import writer
from os import listdir
from os.path import join, exists


# ==============================
# Create report for cache data
# ==============================
def report_cache(cache_list, output_dir):
    with open(join(output_dir, "Reports", "cache_data.csv"), "w", newline="", encoding="utf-8") as f:
        write_data = writer(f)
        write_data.writerow(
            [
                "Filename",
                "URL",
                "URL Length",
                "URL Location",
                "Range URL",
                "Range URL Length",
                "Range URL Location",
                "Cache Entry Location",
                "Ranking Entry Location",
                "Content Size",
                "Content Location",
                "Response Size",
                "Response Location",
                "Entry Creation Time",
                "Range Entry Creation Time",
                "Last Accessed Time",
                "Last Modified Time",
                "Entry Expiry Time",
                "Server Response Time",
                "Server Response",
                "Content Type",
                "Content Encoding",
                "ETag",
                "Max Age",
                "Server Name",
                "Server IP",
                "MD5",
                "SHA1",
                "SHA256",
            ]
        )
        for i in cache_list:
            write_data.writerow(
                [
                    i.filename,
                    i.url,
                    i.url_length,
                    get_location(i.url_location),
                    i.range_url,
                    i.range_url_length,
                    get_location(i.range_url_location),
                    get_location(i.entry_location),
                    get_location(i.rankings_location),
                    i.content_size,
                    get_location(i.content_location),
                    i.response_size,
                    get_location(i.response_location),
                    i.entry_created_time,
                    i.partial_entry_created_time,
                    i.last_accessed_time,
                    i.last_modified_time,
                    i.expiry_time,
                    i.response_time,
                    i.server_response,
                    i.content_type,
                    i.content_encoding,
                    i.etag,
                    i.max_age,
                    i.server_name,
                    i.server_ip,
                    i.md5,
                    i.sha1,
                    i.sha256,
                ]
            )


# ==============================
# Create report for activity log
# ==============================
def report_activity(servers, channels, mails, output_dir):
    elements = max(len(servers), len(channels), len(mails))

    # Fill lists with dashes to maintain uniform length
    for _ in range(elements):
        if len(servers) < elements:
            servers.append("-")
        if len(channels) < elements:
            channels.append("-")
        if len(mails) < elements:
            mails.append("-")

    if elements:
        with open(join(output_dir, "Reports", "activity_data.csv"), "w", newline="", encoding="utf-8") as f:
            write_data = writer(f)
            write_data.writerow(["Servers", "Channels", "Mails"])
            for x in range(elements):
                write_data.writerow([servers[x], channels[x], mails[x]])


# ==============================
# Function to get file location
# ==============================
def get_location(location):
    return f"{location[0]} [{location[1]}]" if location else ""


# ==============================
# Convert chat logs to HTML
# ==============================
def chat_to_html(cache_data_list, output_dir):
    logs_dir = join(output_dir, "Extracted", "Chat_logs")
    chat_list = sorted(listdir(logs_dir))

    for file in chat_list:
        file_path = join(logs_dir, file)

        # Try different encoding formats
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)  # Try normal UTF-8 JSON parsing
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="utf-16") as f:
                    data = json.load(f)  # Try UTF-16
            except UnicodeDecodeError:
                try:
                    with open(file_path, "r", encoding="latin-1") as f:
                        data = json.load(f)  # Try Latin-1 (Windows default)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    print(f"Skipping invalid JSON file: {file_path}")
                    continue  # Skip file if it still fails

        # Check if it's a gzip-compressed file
        try:
            with gzip.open(file_path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, gzip.BadGzipFile):
            pass  # Not a gzip file, move on

        if "messages" in data:
            for e in data["messages"]:
                i = 0
                new_filename = f"{e[0]['channel_id']}.json"
                while exists(join(logs_dir, new_filename)):
                    i += 1
                    new_filename = f"{e[0]['channel_id']} ({i}).json"

                with open(join(logs_dir, new_filename), "w", encoding="utf-8") as f2:
                    json.dump(e, f2, ensure_ascii=False, indent=4)

    print("Chat extraction completed successfully!")
