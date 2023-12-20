#!/usr/bin/env python3

"""
Contains class for dumping Dreamcast data via a httpd-ack server.
"""

from httpd_ack.disc import Disc
from httpd_ack.dreamcast import Dreamcast
import logging
from pathlib import Path
import requests
from tqdm import tqdm
from typing import List

class Dumper:
    """
    Base class for dumping Dreamcast data from a httpd-ack server.

    Contains all major functionality except actually downloading.
    Child classes will handle downloading and displaying progress.
    """
    _download_block_size_bytes = 1024

    def __init__(self,
                 disc: Disc,
                 dreamcast: Dreamcast,
                 server_url: str,
                 output_dir: Path) -> None:
        self.__disc = disc
        self.__dreamcast = dreamcast
        self.__server_url = server_url
        self.__output_dir = output_dir

    @staticmethod
    def _raise_if_invalid_url(file_url: str, file_display_name: str = "Dreamcast file") -> str:
        """
        Checks that the given file URL is valid.
        Returns the file URL if it is valid, or raises errors otherwise.
        """
        if not file_url:
            raise ValueError(f"Unable to find download URL for {file_display_name}!")
        return file_url

    @staticmethod
    def _download_file(file_url: str, output_file: Path, block_size_bytes: int) -> None:
        """
        Performs downloading of files being dumped.
        This is purposely unimplemented in the base class.
        Child classes should override this to download and display progress.
        """
        pass


    def _dump_file(self, file_url: str, file_name_override: str | None = None) -> None:
        """
        Dumps the file at the given URL.
        Configuration of the download is handled by the object data.
        """
        if not self.__server_url in file_url:
            file_url = self.__server_url + '/' + file_url
        # If not overridden, take file name from URL, removing query data
        file_name = file_name_override if file_name_override else Path(file_url).name.split('?')[0]
        output_file = self.__output_dir / file_name
        if not self.__output_dir.exists():
            logging.info(f"Creating output directory at '{self.__output_dir}'...")
            self.__output_dir.mkdir(parents=True)

        self._download_file(file_url, output_file, self._download_block_size_bytes)


    def dump_bios(self) -> None:
        """Dumps the Dreamcast BIOS to the configured output directory."""
        self._dump_file(self._raise_if_invalid_url(self.__dreamcast.bios_url, "Dreamcast BIOS"))


    def dump_disc(self) -> None:
        """Dumps all tracks on the currently inserted Dreamcast disc to the configured output directory."""
        for track in self.__disc.tracks:
            self._dump_file(self._raise_if_invalid_url(track.url, track.name))


    def dump_disc_track(self, track_index: int) -> None:
        """Dumps one track on the currently inserted Dreamcast disc to the configured output directory."""
        max_track_index: int = len(track_index) - 1
        if track_index < 0 or track_index > max_track_index:
            raise ValueError(f"Invalid track index ({track_index}) passed! Valid track indices are 0-{max_track_index}.")
        
        track = self.__disc.tracks[track_index]
        self._dump_file(self._raise_if_invalid_url(track.url, track.name))


    def dump_flash(self) -> None:
        """Dumps the Dreamcast's flash memory to the configured output directory."""
        self._dump_file(self._raise_if_invalid_url(self.__dreamcast.flash_url, "Dreamcast flash"))


    def dump_gdi(self) -> None:
        """Dumps the GDI data of the currently inserted Dreamcast disc to the configured output directory."""
        print(str(self.__disc))
        self._dump_file(self._raise_if_invalid_url(self.__disc.gdi_url, "Disc GDI"))


    def dump_page(self) -> None:
        """Dumps the httpd-ack webpage HTML to the configured output directory."""
        self._dump_file(self._raise_if_invalid_url(self.__server_url, "httpd-ack webpage"), "httpd-ack.html")


    def dump_syscalls(self) -> None:
        """Dumps the Dreamcast's syscalls to the configured output directory."""
        self._dump_file(self._raise_if_invalid_url(self.__dreamcast.syscalls_url, "Dreamcast Syscalls"))


    def dump_multiple(self,
                 dump_bios: bool = False,
                 dump_flash: bool = False,
                 dump_gdi: bool = False,
                 dump_page: bool = False,
                 dump_syscalls: bool = False,
                 dump_disc: bool = False,
                 tracks_to_dump: List[int] = []) -> None:
        """Dumps multiple Dreamcast files to the configured output directory."""
        if dump_bios:
            self.dump_bios()
        if dump_flash:
            self.dump_flash()
        if dump_gdi:
            self.dump_gdi()
        if dump_page:
            self.dump_page()
        if dump_syscalls:
            self.dump_syscalls()

        # Only full disc dumping and track dumping are mutually exclusive
        if dump_disc:
            self.dump_disc()
        elif tracks_to_dump:
            for track_index in tracks_to_dump:
                self.dump_disc_track(track_index)


class ConsoleDumper(Dumper):
    """Class to dump Dreamcast data and output progress to a command-line."""
    @staticmethod
    def _download_file(file_url: str, output_file: Path, block_size_bytes: int) -> None:
        response = requests.get(file_url, stream=True)
        file_size_bytes = int(response.headers.get('content-length', 0))

        logging.info(f"Dumping '{file_url}' to '{output_file}'...")
        progress_bar = tqdm(total=file_size_bytes, unit='B', unit_scale=True)
        with open(output_file, 'wb') as file_data:
            for response_data in response.iter_content(block_size_bytes):
                file_data.write(response_data)
                progress_bar.update(len(response_data))
        progress_bar.close()
