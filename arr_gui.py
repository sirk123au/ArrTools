import csv
import configparser
import urllib.parse
import requests
import tkinter as tk
from tkinter import filedialog, messagebox

CONFIG_PATH = "./config.ini"


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config


def load_defaults():
    config = load_config()
    csv_path = ""
    if config.has_section("gui"):
        csv_path = config.get("gui", "default_csv", fallback="")
    return csv_path


def browse_file(entry):
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


# ----------------------- Radarr helpers ---------------------------------

def radarr_import(csv_path: str, cfg: configparser.ConfigParser) -> None:
    baseurl = cfg["radarr"]["baseurl"]
    urlbase = cfg["radarr"].get("urlbase", "")
    api_key = cfg["radarr"]["api_key"]
    root = cfg["radarr"]["rootfolderpath"]
    profile = cfg["radarr"]["qualityProfileId"]
    search = cfg.getboolean("radarr", "searchForMovie", fallback=False)

    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    session = requests.Session()

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title")
            year = row.get("year")
            imdbid = row.get("imdbid")
            if imdbid:
                url = f"{baseurl}{urlbase}/api/v3/movie/lookup/imdb?imdbId={imdbid}"
            else:
                term = urllib.parse.quote_plus(f"{title} {year}" if year else title)
                url = f"{baseurl}{urlbase}/api/v3/movie/lookup?term={term}"
            rsp = session.get(url, headers=headers)
            if rsp.status_code != 200 or rsp.text in ("", "[]"):
                messagebox.showwarning("Radarr", f"{title} not found")
                continue
            data = rsp.json()
            if isinstance(data, list):
                data = data[0]
            payload = {
                "title": data.get("title"),
                "tmdbId": data.get("tmdbId"),
                "year": data.get("year"),
                "titleSlug": data.get("titleSlug"),
                "qualityProfileId": int(profile),
                "rootFolderPath": root,
                "monitored": True,
                "images": data.get("images", []),
                "addOptions": {"searchForMovie": search},
            }
            add_url = f"{baseurl}{urlbase}/api/v3/movie"
            session.post(add_url, headers=headers, json=payload)


def radarr_export(cfg: configparser.ConfigParser) -> None:
    baseurl = cfg["radarr"]["baseurl"]
    urlbase = cfg["radarr"].get("urlbase", "")
    api_key = cfg["radarr"]["api_key"]
    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    url = f"{baseurl}{urlbase}/api/v3/movie"
    rsp = requests.get(url, headers=headers)
    rsp.raise_for_status()
    data = rsp.json()
    with open("radarr_backup.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "year", "imdbid", "tmdbId"])
        for d in data:
            writer.writerow([d.get("title"), d.get("year"), d.get("imdbId"), d.get("tmdbId")])


# ----------------------- Sonarr helpers ---------------------------------

def sonarr_import(csv_path: str, cfg: configparser.ConfigParser) -> None:
    baseurl = cfg["sonarr"]["baseurl"]
    urlbase = cfg["sonarr"].get("urlbase", "")
    api_key = cfg["sonarr"]["api_key"]
    root = cfg["sonarr"]["rootfolderpath"]
    profile = cfg["sonarr"]["qualityProfileId"]
    search = cfg.getboolean("sonarr", "searchForShow", fallback=False)

    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    session = requests.Session()

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title")
            year = row.get("year")
            imdbid = row.get("imdbid")
            if imdbid:
                url = f"{baseurl}{urlbase}/api/v3/series/lookup?term=imdb:{imdbid}"
            else:
                term = urllib.parse.quote_plus(f"{title} {year}" if year else title)
                url = f"{baseurl}{urlbase}/api/v3/series/lookup?term={term}"
            rsp = session.get(url, headers=headers)
            if rsp.status_code != 200 or rsp.text in ("", "[]"):
                messagebox.showwarning("Sonarr", f"{title} not found")
                continue
            data = rsp.json()
            if isinstance(data, list):
                data = data[0]
            payload = {
                "title": data.get("title"),
                "tvdbId": data.get("tvdbId"),
                "year": data.get("year"),
                "titleSlug": data.get("titleSlug"),
                "qualityProfileId": int(profile),
                "rootFolderPath": root,
                "monitored": True,
                "seasonFolder": True,
                "images": data.get("images", []),
                "seasons": data.get("seasons", []),
                "addOptions": {"searchForMissingEpisodes": search},
            }
            add_url = f"{baseurl}{urlbase}/api/v3/series"
            session.post(add_url, headers=headers, json=payload)


def sonarr_export(cfg: configparser.ConfigParser) -> None:
    baseurl = cfg["sonarr"]["baseurl"]
    urlbase = cfg["sonarr"].get("urlbase", "")
    api_key = cfg["sonarr"]["api_key"]
    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    url = f"{baseurl}{urlbase}/api/v3/series"
    rsp = requests.get(url, headers=headers)
    rsp.raise_for_status()
    data = rsp.json()
    with open("sonarr_backup.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "year", "imdbid"])
        for d in data:
            writer.writerow([d.get("title"), d.get("year"), d.get("imdbId")])


# ----------------------- Lidarr helpers ---------------------------------

def lidarr_import(csv_path: str, cfg: configparser.ConfigParser) -> None:
    baseurl = cfg["lidarr"]["baseurl"]
    api_key = cfg["lidarr"]["api_key"]
    root = cfg["lidarr"]["rootfolderpath"]

    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    session = requests.Session()

    def lookup_artist(name: str) -> str | None:
        url = f"https://api.lidarr.audio/api/v0.4/search?type=artist&query=\"{urllib.parse.quote_plus(name)}\""
        resp = session.get(url, headers=headers)
        if resp.status_code == 200 and resp.text not in ("", "[]"):
            data = resp.json()
            if isinstance(data, list):
                return data[0].get("id")
            return data.get("id")
        return None

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            artist = row.get("artist")
            mbid = row.get("foreignArtistId")
            if not mbid:
                mbid = lookup_artist(artist)
            if not mbid:
                messagebox.showwarning("Lidarr", f"{artist} not found")
                continue
            payload = {
                "artistName": artist,
                "foreignArtistId": mbid,
                "QualityProfileId": 1,
                "MetadataProfileId": 1,
                "Path": os.path.join(root, artist),
                "RootFolderPath": root,
                "monitored": True,
                "addOptions": {"searchForMissingAlbums": False},
            }
            add_url = f"{baseurl}/api/v1/artist"
            session.post(add_url, headers=headers, json=payload)


def lidarr_export(cfg: configparser.ConfigParser) -> None:
    baseurl = cfg["lidarr"]["baseurl"]
    api_key = cfg["lidarr"]["api_key"]
    headers = {"Content-type": "application/json", "X-Api-Key": api_key}
    url = f"{baseurl}/api/v1/artist"
    rsp = requests.get(url, headers=headers)
    rsp.raise_for_status()
    data = rsp.json()
    with open("lidarr_backup.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["artist", "foreignArtistId"])
        for d in data:
            writer.writerow([d.get("artistName"), d.get("foreignArtistId")])


# ----------------------- GUI logic ---------------------------------

def run_action(service_var, action_var, csv_entry):
    service = service_var.get()
    action = action_var.get()
    csv_path = csv_entry.get()

    cfg = load_config()

    if action == "Import" and not csv_path:
        messagebox.showerror("Error", "Please select a CSV file for import")
        return

    try:
        if service == "Radarr" and action == "Import":
            radarr_import(csv_path, cfg)
        elif service == "Radarr" and action == "Export":
            radarr_export(cfg)
        elif service == "Sonarr" and action == "Import":
            sonarr_import(csv_path, cfg)
        elif service == "Sonarr" and action == "Export":
            sonarr_export(cfg)
        elif service == "Lidarr" and action == "Import":
            lidarr_import(csv_path, cfg)
        elif service == "Lidarr" and action == "Export":
            lidarr_export(cfg)
        else:
            messagebox.showerror("Error", "Invalid selection")
            return
        messagebox.showinfo("Success", "Operation completed")
    except Exception as exc:  # simplistic error handling
        messagebox.showerror("Error", str(exc))


def main():
    root = tk.Tk()
    root.title("ArrTools GUI")

    csv_default = load_defaults()

    tk.Label(root, text="Service:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    service_var = tk.StringVar(value="Radarr")
    tk.OptionMenu(root, service_var, "Radarr", "Sonarr", "Lidarr").grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Action:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    action_var = tk.StringVar(value="Import")
    tk.OptionMenu(root, action_var, "Import", "Export").grid(row=1, column=1, padx=5, pady=5)

    tk.Label(root, text="CSV File:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    csv_entry = tk.Entry(root, width=40)
    csv_entry.grid(row=2, column=1, padx=5, pady=5)
    csv_entry.insert(0, csv_default)
    tk.Button(root, text="Browse", command=lambda: browse_file(csv_entry)).grid(row=2, column=2, padx=5, pady=5)

    tk.Button(
        root,
        text="Run",
        command=lambda: run_action(service_var, action_var, csv_entry),
    ).grid(row=3, column=0, columnspan=3, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
