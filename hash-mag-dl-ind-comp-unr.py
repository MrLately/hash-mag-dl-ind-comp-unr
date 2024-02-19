import requests
import time

torrent_hash = "5990e29607c45d2027fb614bc621218b1ae706c6"  # Example hash for complete series
real_debrid_api_token = ""
headers = {"Authorization": f"Bearer {real_debrid_api_token}"}

def generate_magnet_link(hash):
    return f"magnet:?xt=urn:btih:{hash}"

def add_magnet_to_realdebrid(hash):
    magnet = generate_magnet_link(hash)
    response = requests.post("https://api.real-debrid.com/rest/1.0/torrents/addMagnet", headers=headers, data={"magnet": magnet})
    response.raise_for_status()
    return response.json()['id']

def select_largest_file_and_start_download(torrent_id):
    response = requests.get(f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}", headers=headers)
    response.raise_for_status()
    files_info = response.json()['files']

    video_files = [file for file in files_info if file['path'].lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    if video_files:
        largest_video_file = sorted(video_files, key=lambda x: x['bytes'], reverse=True)[0]['id']
        response = requests.post(f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}", headers=headers, data={"files": str(largest_video_file)})
        response.raise_for_status()
    else:
        print("No video files found in torrent.")

def select_all_video_files_and_start_download(torrent_id):
    response = requests.get(f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}", headers=headers)
    response.raise_for_status()
    files_info = response.json()['files']

    video_files = [file for file in files_info if file['path'].lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    if video_files:
        video_file_ids = [str(file['id']) for file in video_files]
        selected_files = ",".join(video_file_ids)
        
        response = requests.post(f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}", headers=headers, data={"files": selected_files})
        response.raise_for_status()
    else:
        print("No video files found in torrent.")

def check_download_status(torrent_id):
    while True:
        response = requests.get(f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}", headers=headers)
        response.raise_for_status()
        torrent_info = response.json()
        if torrent_info['status'] == 'downloaded':
            download_links = torrent_info['links']
            return download_links
        time.sleep(10)

def unrestrict_links(download_links):
    unrestricted_links = []
    for download_link in download_links:
        response = requests.post("https://api.real-debrid.com/rest/1.0/unrestrict/link", headers=headers, data={"link": download_link})
        response.raise_for_status()
        unrestricted_links.append(response.json()['download'])
    return unrestricted_links

def main(download_all_files=False):
    torrent_id = add_magnet_to_realdebrid(torrent_hash)
    print(f"Torrent hash added successfully, torrent ID: {torrent_id}")
    
    if download_all_files:
        select_all_video_files_and_start_download(torrent_id)
        print("All video files in torrent selected and download started.")
    else:
        select_largest_file_and_start_download(torrent_id)
        print("Largest video file in torrent selected and download started.")
    
    download_links = check_download_status(torrent_id)
    if not download_all_files:
        download_links = [download_links[0]]
    #print(f"Download link(s) obtained: {download_links}")
    print(f"Download link(s) obtained")
    print("Getting unrestricted links")
    
    unrestricted_links = unrestrict_links(download_links)
    print(f"Unrestricted Direct Download Link(s): {unrestricted_links}")
    

if __name__ == "__main__":
    main(download_all_files=True)  # Change to False to download only the largest file when using hash for individual show, True to download complete series.
