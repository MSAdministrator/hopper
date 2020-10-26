from email.parser import HeaderParser
from .parser import Parser
from .utils import cleanup_text, decode_and_convert_to_unicode


class Hopper:

    def __init__(self):
        self.parser = Parser()

    def analyse(self, raw_headers):
        """
        sample output:
        {
            'To': u'robin@apple.com',
            'From': u'Dhruv <dhruv@foo.com>',
            'Cc': u'Shivam <shivam@foo.com>',
            'Bcc': u'Abhishek <quirk@foo.com>',
            'total_delay': 2,
            'trail': [
                {
                    'from': '',
                    'protocol': 'HTTP',
                    'receivedBy': '10.31.102.130',
                    'timestamp': 1452574216,
                    'delay': 0
                },
                {
                    'from': '',
                    'protocol': 'SMTP',
                    'receivedBy': 'mail-vk0-x22b.google.com',
                    'timestamp': 1452574218,
                    'delay': 2
                },
                {
                    'from': 'mail-vk0-x22b.google.com',
                    'protocol': 'ESMTPS',
                    'receivedBy': 'mx.google.com',
                    'timestamp': 1452574218,
                    'delay': 0
                },
                {
                    'from': '',
                    'protocol': 'SMTP',
                    'receivedBy': '10.66.77.65',
                    'timestamp': 1452574218,
                    'delay': 0
                }
            ]
        }
        """
        if raw_headers is None:
            return None
        raw_headers = raw_headers.strip()
        parser = HeaderParser()
        headers = parser.parsestr(raw_headers)#.encode('ascii', 'ignore'))
        received_headers = headers.get_all('Received')
        trail = self.__generate_trail(received_headers)
        analysis = {
            'From': decode_and_convert_to_unicode(headers.get('From')),
            'To': decode_and_convert_to_unicode(headers.get('To')),
            'Cc': decode_and_convert_to_unicode(headers.get('Cc')),
            'Bcc': decode_and_convert_to_unicode(headers.get('Bcc')),
            'trail': trail,
            'total_delay': sum([hop['delay'] for hop in trail]) if trail else 0
        }
        return analysis

    def __generate_trail(self, received):
        """
        Takes a list of `received` headers and
        creates the email trail (structured information of hops in transit)
        """
        if received is None:
            return None

        received = [cleanup_text(header) for header in received]
        trail = [self.__analyse_hop(header) for header in received]

        # sort in chronological order
        trail.reverse()
        trail = self.__set_delay_information(trail)
        return trail

    def __analyse_hop(self, header):
        """ Parses the details associated with the hop into a structured format """
        return {
            "from": self.parser.extract_from_label(header),
            "receivedBy": self.parser.extract_received_by_label(header),
            "protocol": self.parser.extract_protocol(header),
            "timestamp": self.parser.extract_timestamp(header)
        }

    def __set_delay_information(self, hop_list):
        """ For each hop sets the calculated `delay` from previous hop | mutates list"""
        previous_timestamp = None
        for hop in hop_list:
            hop['delay'] = self.parser.calculate_delay(hop['timestamp'], previous_timestamp)
            previous_timestamp = hop['timestamp']
        return hop_list
