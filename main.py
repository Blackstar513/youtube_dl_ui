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
    sg.theme('Dark Blue 3')

    layout = [[sg.Text("Youtube-dl Configurations)")],
              [sg.Text("Video/Playlist URL"), sg.Input(key="URL"), sg.Checkbox("is Playlist?", default=False, key="Playlist")],
              [sg.Text("Target Folder"), sg.Input(key="Folder"), sg.FolderBrowse()],
              [sg.Text("Filename"), sg.Input("%(title)s", key="Filename")],
              [sg.Text("File Format"), sg.Combo(["mp4", "mp3", "wav", "3gp", "aac", "flv", "m4a", "ogg", "webm"], key="Format")],
              [sg.Text("Other Options"), sg.Input(key="Other")],
              [sg.OK(), sg.Cancel()]]

    window = sg.Window('Get filename example', layout)
    event, values = window.read()
    window.close()

    if event == "OK":
        is_playlist = "--yes-playlist" if values["Playlist"] else "--no-playlist"
        file_format = values["Format"]
        full_path = f'{values["Folder"]}/{values["Filename"]}.%(ext)s'

        options = [is_playlist, "-o", full_path]
        if file_format == "mp3" or file_format == "wav"\
                or file_format == "aac" or file_format == "m4a":
            options += ["--extract-audio", "--audio-format", file_format]
        else:
            options += ["-f", file_format]

        if values["Other"]:
            options += values["Other"].split(" ")

        return options, values["URL"]
    else:
        sys.exit(0)



def main():
    sg.theme('Dark Blue 3')
    youtube_dl_executable = download_youtube_dl("./downloader")

    options, url = configure_youtube_dl()

    print(f"Optionen: {options}\nURL: {url}")

    cmd_list = [youtube_dl_executable] + options + [url]
    print(cmd_list)

    process = subprocess.Popen(cmd_list,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)

    while True:
        output = process.stdout.readline()
        error_out = process.stderr.readline()
        if process.poll() is not None:
            return
        if output:
            sg.Print(output.strip())
        if error_out:
            sg.popup_error(error_out)


if __name__ == "__main__":
    main()
