import string
import pytz
import dateparser
import re
import calendar
from .utils import cleanup_text


class Parser:

    def extract_timestamp(self, header):
        return self.get_timestamp(self.extract_timestring(header))

    def extract_from_label(self, header):
        """ Get the hostname associated with `from` """
        match = re.findall(
            """
            from\s+
            (.*?)
            (?:\s+|$)
            """, header, re.DOTALL | re.X)
        return match[0] if match else ''

    def extract_received_by_label(self, header):
        """ Get the hostname associated with `by` """
        header = re.sub('\n', ' ', header)
        header = self.remove_details(header)
        header = cleanup_text(header)

        if header.startswith('from'):
            match = re.findall('from\s+(?:.*?)\s+by\s+(.*?)(?:\s+|$)', header)
            return match[0] if match else ''
        elif header.startswith('by'):
            match = re.findall('by\s+(.*?)(?:\s+|$)', header)
            return match[0] if match else ''
        return ''

    def extract_protocol(self, header):
        """ Get the protocol used. e.g. SMTP, HTTP etc. """
        header = re.sub('\n', ' ', header)
        header = self.remove_details(header)
        header = cleanup_text(header)

        protocol = ''

        if header.startswith('from'):
            match = re.findall(
                """
                from\s+(?:.*?)\s+by\s+(?:.*?)\s+
                (?:
                    (?:with|via)
                    (.*?)
                    (?:id|$|;)
                    |id|$
                )
                """, header, re.DOTALL | re.X)
            protocol = match[0] if match else ''
        if header.startswith('by'):
            match = re.findall(
                """
                by\s+(?:.*?)\s+
                (?:
                    (?:with|via)
                    (.*?)
                    (?:id|$|;)
                    |id|$
                )
                """, header, re.DOTALL | re.X)
            protocol = match[0] if match else ''

        return cleanup_text(protocol)

    def extract_timestring(self, header):
        """
        Tries to extract a timestring from a header
        Returns None or a String that *could* be a valid timestring
        """
        if type(header) != str:
            raise TypeError

        header = cleanup_text(header)
        timestring = None

        split_by_semicolon = header.split(';')
        split_by_newline = header.split('\n')
        split_by_id = re.split('\s+id\s+[^\s]*\s+', header)

        if len(split_by_semicolon) > 1:
            timestring = split_by_semicolon[-1]
        elif len(split_by_semicolon) == 1:
            if len(split_by_newline) > 1:
                # find it on the last line
                timestring = split_by_newline[-1]
            elif len(split_by_id) > 1:
                # find it after` id abc.xyz `
                timestring = split_by_id[-1]

        if timestring is None:
            return None

        timestring = cleanup_text(timestring)
        timestring = cleanup_text(self.remove_details(timestring))
        timestring = self.strip_timezone_name(timestring)
        timestring = re.sub('-0000', '+0000', timestring)

        return timestring
    
    def remove_details(self, text):
        return re.sub('([(].*?[)])', ' ', text)

    def strip_timezone_name(self, timestring):
        """ Removes extra timezone name at the end. eg: "-0800 (PST)" -> "-0800" """
        pattern = '([+]|[-])([0-9]{4})[ ]([(]([a-zA-Z]{3,4})[)]|([a-zA-Z]{3,4}))'
        if re.search(pattern, timestring) is None:
            return timestring

        split = timestring.split(' ')
        split.pop()
        return string.join(split, ' ')

    def get_timestamp(self, timestring):
        """ Convert a timestring to unix timestamp """
        if timestring is None:
            return None
        date = dateparser.parse(timestring)
        if date is None:
            return None
        date = date.astimezone(pytz.utc)
        return calendar.timegm(date.utctimetuple())

    def calculate_delay(self, current_timestamp, previous_timestamp):
        """ Returns delay for two unix timestamps """
        if current_timestamp is None or previous_timestamp is None:
            return 0
        delay = current_timestamp - previous_timestamp
        if delay < 0:
            # It's not possible for the current server to receive the email before previous one
            # It means that either one or both of the servers clocks are off.
            # We assume a delay of 0 in this case
            delay = 0
        return delay

    def get_path_delay(self, current, previous, timestamp_parser=get_timestamp, timestring_parser=extract_timestring):
        """
        Returns calculated delay (in seconds)  between two subsequent 'Received' headers
        Returns None if not determinable
        """
        current_timestamp = timestamp_parser(timestring_parser(current))
        previous_timestamp = timestamp_parser(timestring_parser(previous))

        if current_timestamp is None or previous_timestamp is None:
            # parsing must have been unsuccessful, can't do much here
            return None

        return self.calculate_delay(current_timestamp, previous_timestamp)
