#!/usr/bin/env python3

"""
Contains class for containing and display httpd-ack disc data.
"""

from typing import Any, List

class Track:
    """
    Contains Dreamcast disc track info as found by httpd-ack.
    """
    def __init__(self, url: str, name: str, start: int, end: int, size: int) -> None:
        self.url = url
        self.name = name
        self.sector_start = start
        self.sector_end = end
        self.size = size


    def __repr__(self):
        return f'Track(\'{self.url}\', \'{self.name}\', {self.sector_start}, {self.sector_end}, {self.size})'


    def __str__(self):
        return self.get_table_string()
    

    @staticmethod
    def get_table_divider() -> str:
        """Returns the string for dividing the Track header & data in a stringified table."""
        return "------------ | ------------ | ---------- | ----------- | ---------------"

    @staticmethod
    def get_table_header() -> str:
        """Returns the header string for displaying Track data in a stringified table."""
        return "Name         | Start Sector | End Sector | Size        | URL"


    def get_table_string(self) -> str:
        """Returns a string for displaying Track data in a stringified table."""
        return f"{self.name:<12} | {self.sector_start:<12} | {self.sector_end:<10} | {self.size:<11} | {self.url}"



class Disc:
    """
    Contains Dreamcast disc info as found by httpd-ack.
    """
    _display_to_property_name = {
        'Title': 'title',
        'Media ID': 'media_id',
        'Media Config': 'media_config',
        'Regions': 'region',
        'Peripheral String': 'peripheral_string',
        'Product Number': 'product_number',
        'Version': 'version',
        'Release Date': 'release_date',
        'Manufacturer ID': 'manufacturer_id',
        'TOC': 'toc'
    }


    def __init__(self) -> None:
        self.is_dreamcast_disc = True
        self.title = "Unknown"
        self.media_id = "Unknown"
        self.media_config = "Unknown"
        self.region = "Unknown"
        self.peripheral_string = "Unknown"
        self.product_number = "Unknown"
        self.version = "Unknown"
        self.release_date = "Unknown"
        self.manufacturer_id = "Unknown"
        self.toc = "Unknown"
        self.tracks: List[Track] = []
        self.gdi_url = None


    def __str__(self):
        disc_type = "Dreamcast" if self.is_dreamcast_disc else "Non-Dreamcast"
        disc_strs = [
            f"Disc Type: {disc_type}",
            f"Title: {self.title}",
            f"Media ID: {self.media_id}",
            f"Media Config: {self.media_config}",
            f"Region: {self.region}",
            f"Peripheral String: {self.peripheral_string}",
            f"Product Number: {self.product_number}",
            f"Version: {self.version}",
            f"Release Date: {self.release_date}",
            f"Manufacturer ID: {self.manufacturer_id}",
            f"Table of Contents: {self.toc}",
            f"GDI URL: {self.gdi_url}" if self.gdi_url else "GDI: Not Available"
        ]

        track_strs = [f"\t{track.get_table_string()}" for track in self.tracks]
        track_strs.insert(0, "Tracks:")
        track_strs.insert(1, f"\t{Track.get_table_header()}")
        track_strs.insert(2, f"\t{Track.get_table_divider()}")

        return '\n'.join(disc_strs + track_strs)


    def add_track(self, track: Track) -> None:
        """Adds a new track object to this disc."""
        self.tracks.append(track)


    def set_property(self, display_name: str, value: Any) -> bool:
        """
        Sets the value of one of this disc's properties by name.
        Returns True if the property was set, False otherwise.
        """
        prop_name = self._display_to_property_name.get(display_name)

        # Parser attempts to set Dreamcast data here, so unfound properties are normal.
        if prop_name:
            setattr(self, prop_name, value)
            return True
        return False
