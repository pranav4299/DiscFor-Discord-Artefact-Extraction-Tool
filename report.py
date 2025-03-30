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
        write_data.writerow([
            "Filename", "URL", "URL Length", "URL Location", "Range URL",
            "Range URL Length", "Range URL Location", "Cache Entry Location",
            "Ranking Entry Location", "Content Size", "Content Location",
            "Response Size", "Response Location", "Entry Creation Time",
            "Range Entry Creation Time", "Last Accessed Time", "Last Modified Time",
            "Entry Expiry Time", "Server Response Time", "Server Response",
            "Content Type", "Content Encoding", "ETag", "Max Age", "Server Name",
            "Server IP", "MD5", "SHA1", "SHA256",
        ])
        for i in cache_list:
            write_data.writerow([
                i.filename, i.url, i.url_length, get_location(i.url_location),
                i.range_url, i.range_url_length, get_location(i.range_url_location),
                get_location(i.entry_location), get_location(i.rankings_location),
                i.content_size, get_location(i.content_location), i.response_size,
                get_location(i.response_location), i.entry_created_time,
                i.partial_entry_created_time, i.last_accessed_time,
                i.last_modified_time, i.expiry_time, i.response_time,
                i.server_response, i.content_type, i.content_encoding,
                i.etag, i.max_age, i.server_name, i.server_ip,
                i.md5, i.sha1, i.sha256,
            ])


# ==============================
# Create report for activity log
# ==============================
def report_activity(servers, channels, mails, output_dir):
    elements = max(len(servers), len(channels), len(mails))
    servers.extend(["-"] * (elements - len(servers)))
    channels.extend(["-"] * (elements - len(channels)))
    mails.extend(["-"] * (elements - len(mails)))

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
        data = None

        # Try to detect if file is compressed
        try:
            with open(file_path, "rb") as f:
                first_bytes = f.read(2)
            
            if first_bytes.startswith(b"\x1f\x8b"):  # Gzip magic number
                with gzip.open(file_path, "rt", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"✔ Decompressed and loaded: {file_path}")
        except Exception as e:
            print(f"⚠ Error reading Gzip file {file_path}: {e}")

        # If not Gzip, try reading as plain JSON
        if data is None:
            for encoding in ["utf-8", "utf-16", "latin-1", "iso-8859-1"]:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        data = json.load(f)
                    print(f"✔ Successfully loaded {file_path} with encoding {encoding}")
                    break
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue  # Try the next encoding
                except Exception as e:
                    print(f"⚠ Error reading {file_path} with {encoding}: {e}")

        # If data is still None, skip the file
        if data is None:
            print(f"❌ Skipping unreadable file: {file_path}")
            continue

        # If valid JSON, process chat logs
        if "messages" in data:
            for e in data["messages"]:
                i = 0
                new_filename = f"{e[0]['channel_id']}.json"
                while exists(join(logs_dir, new_filename)):
                    i += 1
                    new_filename = f"{e[0]['channel_id']} ({i}).json"

                with open(join(logs_dir, new_filename), "w", encoding="utf-8") as f2:
                    json.dump(e, f2, ensure_ascii=False, indent=4)

    print("✅ Chat extraction completed successfully!")
