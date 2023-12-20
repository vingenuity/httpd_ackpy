#!/usr/bin/env python3

"""
Contains class for parsing httpd-ack HTML text.
"""

from enum import IntEnum
from html.parser import HTMLParser
from httpd_ack.disc import Disc, Track
from httpd_ack.dreamcast import Dreamcast
from pathlib import Path
from typing import Any, List, Tuple
from urllib.request import urlopen

class TableParseTime(IntEnum):
    """Enumerates the times in which the table is parsed versus other data."""
    Before = -1,
    During = 0,
    After = 1


class HttpdAckParser(HTMLParser):
    """
    Parses httpd-ack HTML data.
    Dreamcast console, disc, and information about the http-ack server are parsed.
    """
    def __init__(self):
        HTMLParser.__init__(self)

        # Final Data
        self.__disc = Disc()
        self.__dreamcast = Dreamcast()
        self.__server_url = None
        self.__server_version = None

        # Parsing State
        self.__table_parse_time = TableParseTime.Before
        self.__in_table_header = False
        self.__subtable = None
        self.__table_cell_index = None
        self.__table_row_data = []
            

    def _is_non_dreamcast_disc_warning(self, row_data: List[Any]) -> bool:
        """Returns whether the given row data contains a non-Dreamcast disc warning."""
        if len(row_data) != 1:
            return False
        
        return "Not Dreamcast disc" in str(row_data)
            

    def _is_table_header_attrs(self, attrs: List[Tuple[str, str]]) -> bool:
        """Returns whether the given attributes are used in httpd-ack table headers."""
        for attr_name, attr_value in attrs:
            if attr_name == 'bgcolor' and attr_value == '#CCCCCC':
                return True
        
        return False


    def get_disc_data(self) -> Disc:
        """Returns the Dreamcast disc data parsed by this parser."""
        return self.__disc


    def get_dreamcast_data(self) -> Disc:
        """Returns the Dreamcast data parsed by this parser."""
        return self.__dreamcast


    def get_server_url(self) -> str:
        """Returns the httpd-ack server version parsed by this parser."""
        return self.__server_url


    def get_server_version(self) -> str:
        """Returns the httpd-ack server version parsed by this parser."""
        return self.__server_version


    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        match tag:
            case 'table':
                self.__table_parse_time = TableParseTime.During

            case 'tr':
                assert(self.__table_parse_time == TableParseTime.During)
                if self.__table_cell_index != None: # Missing </tr> tag
                    self._handle_table_row_end(self.__subtable, self.__table_row_data)

                self.__in_table_header = self._is_table_header_attrs(attrs)
                self.__table_cell_index = 0
                self.__table_row_data = []

            case 'td':
                assert(self.__table_parse_time == TableParseTime.During)
                self.__in_table_cell = True
                self.__in_table_header = self.__in_table_header or self._is_table_header_attrs(attrs)

            case 'a':
                if self.__in_table_cell:
                    for attr_name, attr_value in attrs:
                        if attr_name == 'href':
                            self.__table_row_data.append(attr_value)

            case _:
                return
        

    def handle_endtag(self, tag: str) -> None:
        match tag:
            case 'table':
                self.__table_parse_time = TableParseTime.After

            case 'tr':
                assert(self.__table_parse_time == TableParseTime.During)
                self._handle_table_row_end(self.__subtable, self.__table_row_data)

            case 'td':
                assert(self.__table_parse_time == TableParseTime.During)
                self.__table_cell_index += 1
                self.__in_table_cell = False

            case _:
                return


    def handle_data(self, data: str) -> None:
        if self.__table_parse_time == TableParseTime.Before:
            return

        if self.__table_parse_time == TableParseTime.After:
            if ' server' in data:
                self.__server_version = data.removeprefix('httpd-ack v').removesuffix(' server')
            return

        if self.__table_cell_index is None:
            return

        if self.__in_table_header:
            if self.__table_cell_index == 0:
                self.__subtable = data.lower()
            return

        if self.__in_table_cell:
            self.__table_row_data.append(data)


    def _handle_table_row_end(self, subtable_name: str, row_data: List[Any]) -> None:
        """Handles the end of a row in the httpd-ack HTML tables."""
        self.__table_cell_index = None

        if self.__in_table_header:
            self.__in_table_header = False
            return
        
        # If we're not in a header, apply the values we've found
        match subtable_name:
            case 'cd-rom':
                if self._is_non_dreamcast_disc_warning(row_data):
                    self.__disc.is_dreamcast_disc = False
                else:
                    self.__disc.set_property(*row_data)

            case 'track':
                self.__disc.add_track(Track(*row_data))
                pass

            case 'misc':
                # Try setting the Dreamcast property first, as 3/4 misc rows are DC data
                property_was_set = self.__dreamcast.set_url_property(*row_data)
                if property_was_set:
                    return
                # warn if this isn't found
                self.__disc.gdi_url = row_data[0]
            
            case _:
                assert False, "Ended table row with unexpected subtable name '%s" % subtable_name


    def parse_from_file(self, file: Path) -> None:
        """Parses the httpd-ack HTML file at the given path."""
        if not file.exists():
            raise FileNotFoundError(f"Unable to find file at '{file}'!")

        self.__server_url = str(file)
        html_text = file.read_text()
        self.feed(html_text)


    def parse_from_server(self, server_url: str) -> None:
        """Parses the httpd-ack HTML file at the given path."""
        self.__server_url = server_url

        with urlopen(server_url) as html_data:
            html_bytes = html_data.read()
            html_text = html_bytes.decode()
            self.feed(html_text)
