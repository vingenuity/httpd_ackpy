#!/usr/bin/env python3

"""
Contains class for containing and display httpd-ack Dreamcast data.
"""

class Dreamcast:
    """
    Contains Dreamcast info as found by httpd-ack.
    """
    _file_to_property_name = {
        'dc_bios.bin': 'bios_url',
        'dc_flash.bin': 'flash_url',
        'syscalls.bin': 'syscalls_url',
    }

    def __init__(self) -> None:
        self.bios_url = None
        self.flash_url = None
        self.syscalls_url = None


    def __repr__(self):
        return f'Dreamcast(\'{self.bios_url}\', \'{self.flash_url}\', {self.syscalls_url})'


    def __str__(self):
        table_strs = [
            "Name     | Memory Addresses        | File Name    | URL",
            "-------- | ----------------------- | ------------ | ------------------",
            f"BIOS     | 0x00000000 - 0x001FFFFF | dc_bios.bin  | {self.bios_url}",
            f"Flash    | 0x00200000 - 0x0021FFFF | dc_flash.bin | {self.flash_url}",
            f"Syscalls | 0x8C000000 - 0x8C007FFF | syscalls.bin | {self.syscalls_url}"
        ]
        return '\n'.join(table_strs)


    def set_url_property(self, url: str, file_name: str, _: str) -> bool:
        """
        Sets the value of one of this Dreamcast's URL properties by name.
        Returns True if the property was set, False otherwise.
        NOTE: The name/value order is swapped due to HTML parsing order!
        """
        prop_name = self._file_to_property_name.get(file_name)

        # Parser attempts to set Disc data here, so unfound properties are normal.
        if prop_name:
            setattr(self, prop_name, url)
            return True
        return False
