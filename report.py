# List of standard library imports
from csv import writer
from json import dump, load
from os import listdir
from os.path import join, exists

# This script contains functions responsible for creation of reports

# Create report for data recovered from cache
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
            "Content Type", "Content Encoding", "ETag", "Max Age",
            "Server Name", "Server IP", "MD5", "SHA1", "SHA256"
        ])
        for i in cache_list:
            write_data.writerow([
                i.filename, i.url, i.url_length, get_location(i.url_location),
                i.range_url, i.range_url_length, get_location(i.range_url_location),
                get_location(i.entry_location), get_location(i.rankings_location),
                i.content_size, get_location(i.content_location),
                i.response_size, get_location(i.response_location),
                i.entry_created_time, i.partial_entry_created_time,
                i.last_accessed_time, i.last_modified_time, i.expiry_time,
                i.response_time, i.server_response, i.content_type,
                i.content_encoding, i.etag, i.max_age, i.server_name,
                i.server_ip, i.md5, i.sha1, i.sha256
            ])

def get_location(location):
    return f"{location[0]} [{location[1]}]" if location else ""

# Create report for data recovered from activity log
def report_activity(servers, channels, mails, output_dir):
    elements = max(len(servers), len(channels), len(mails))
    
    # Fill lists with dashes to avoid index errors
    servers += ["-"] * (elements - len(servers))
    channels += ["-"] * (elements - len(channels))
    mails += ["-"] * (elements - len(mails))
    
    if elements:
        with open(join(output_dir, "Reports", "activity_data.csv"), "w", newline="", encoding="utf-8") as f:
            write_data = writer(f)
            write_data.writerow(["Servers", "Channels", "Mails"])
            for x in range(elements):
                write_data.writerow([servers[x], channels[x], mails[x]])

# Create chat log reports in form of HTML files
def chat_to_html(cache_data_list, output_dir):
    logs_dir = join(output_dir, "Extracted", "Chat_logs")
    chat_list = sorted(listdir(logs_dir))

    for file in chat_list:
        with open(join(logs_dir, file), "r", encoding="utf-8") as f:
            data = load(f)

        if "messages" in data:
            for e in data["messages"]:
                i = 0
                new_filename = f"{e[0]['channel_id']}.json"
                while exists(join(logs_dir, new_filename)):
                    i += 1
                    new_filename = f"{e[0]['channel_id']} ({i}).json"

                with open(join(logs_dir, new_filename), "w", encoding="utf-8") as f2:
                    dump(e, f2, ensure_ascii=False, indent=4)

    for file in chat_list:
        filename = file.split(".", 1)[0]
        messages = ""

        html_struct = f"""<!DOCTYPE html>
<html>
<head>
<style>
table, th, td{{border: 1px solid black;}}
</style>
</head>
<body>
<h1>Channel Id: {filename}</h1>
%s
</body>
</html>
"""

        with open(join(logs_dir, file), "r", encoding="utf-8") as f:
            data = load(f)

        if any("channel_id" in s for s in data):
            for e in data:
                avatar_path = ""
                att_path = ""
                img_url = ""

                avatar = e["author"].get("avatar")
                if avatar and exists(join(output_dir, "Extracted", "Images", f"{avatar}.webp")):
                    avatar_path = join(output_dir, "Extracted", "Images", f"{avatar}.webp")

                date, time = e["timestamp"].split("T", 1)
                time = time.split(".", 1)[0]
                timestamp = f"{date} {time}"

                if e["attachments"]:
                    url = e["attachments"][0]["url"].split("attachments", 1)[1]
                    for key in cache_data_list:
                        if url in key.url:
                            att_file = key.filename
                            img_url = key.url
                            if exists(join(output_dir, "Extracted", "Images", att_file)):
                                att_path = join(output_dir, "Extracted", "Images", att_file)
                                break

                message = f"""<table width="100%">
<tr><th width="30%" align="center">Message Id</th><td>{e["id"]}</td><th>Time</th><td width="30%">{timestamp}</td></tr>
<tr><th rowspan="3">Author</th>
<th>Id</th><td>{e["author"]["id"]}</td>
<td rowspan="3"><img src="{avatar_path}" alt="{e["author"].get("avatar", '')}" width="50px" height="50px"></td></tr>
<tr><th>Username</th><td>{e["author"]["username"]}</td></tr>
<tr><th>Discriminator</th><td>{e["author"]["discriminator"]}</td></tr>
<tr width="100%"><th>Content</th><td colspan="3">{e["content"]}</td></tr>
<tr><td colspan="4" align="center"><img src="{att_path}" alt="{url}" class="center"></td></tr>
<tr><td colspan="4" align="center">{img_url}</td></tr>
</table>
<br/>
"""

                messages += message

        if messages:
            html_file = html_struct % messages
            with open(join(output_dir, "Reports", "Chat_logs", f"{filename}.html"), "w", encoding="utf-8") as report:
                report.write(html_file)
