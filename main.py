from platform import system
from os import chmod
from pathlib import Path
import urllib.request
import PySimpleGUI as sg
import sys
import subprocess
# import youtube_dl


def already_downloaded(directory: str) -> bool:
    if system() == "Linux":
        p = Path(f"{directory}/youtube-dl")
        return p.exists()
    elif system() == "Windows":
        p = Path(f"{directory}/youtube-dl.exe")
        return p.exists()
    else:
        raise OSError("Unsupported OS")


def download_youtube_dl(directory: str) -> str:
    Path(directory).mkdir(parents=True, exist_ok=True)

    filename = "youtube-dl"
    if system() == "Windows":
        filename = f"{filename}.exe"

    dir_file = f"{directory}/{filename}"

    if not already_downloaded(directory):
        urllib.request.urlretrieve(f"https://yt-dl.org/downloads/latest/{filename}", dir_file,
                                   reporthook=download_progress_bar)

        if system() == "Linux":
            chmod(dir_file, 0o0555)

    return dir_file


def download_progress_bar(count_blocks, block_size, total_size):
    sg.one_line_progress_meter("Download", count_blocks * block_size, total_size, "Downloading Youtube-dl",
                               orientation="h", key="download")


def configure_youtube_dl() -> (list, str):
    options = ""
    url = ""
    sg.theme('Dark Blue 3')

    layout = [[sg.Text("Youtube-dl Configurations)")],
              [sg.Text("Target Folder"), sg.Input(key="Folder"), sg.FolderBrowse()],
              [sg.Text("Filename with extension"), sg.Input(key="Filename")],
              [sg.Text("Video/Playlist URL"), sg.Input(key="URL"), sg.Checkbox("is Playlist?", default=False, key="Playlist")],
              [sg.Text("Other Options"), sg.Input(default_text="", key="Other")],
              [sg.OK(), sg.Cancel()]]

    window = sg.Window('Get filename example', layout)
    event, values = window.read()
    window.close()

    if event == "OK":
        is_playlist = "--yes-playlist" if values["Playlist"] else "--no-playlist"
        full_path = f'{values["Folder"]}/{values["Filename"]}'
        options = f'{is_playlist} -o "{full_path}"'

        url = values["URL"]
    else:
        sys.exit(0)

    return [is_playlist, "-o", full_path], url


def main():
    sg.theme('Dark Blue 3')
    youtube_dl_executable = download_youtube_dl("./downloader")

    options, url = configure_youtube_dl()

    print(f"Optionen: {options}\nURL: {url}")

    cmd_list = [youtube_dl_executable] + options + [url]
    print(cmd_list)

    process = subprocess.Popen(cmd_list,
                               stdout=subprocess.PIPE,
                               universal_newlines=True)

    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            return
        if output:
            sg.Print(output.strip())


if __name__ == "__main__":
    main()
