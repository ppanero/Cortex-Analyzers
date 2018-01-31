#!/usr/bin/env python
import pypdns
import ipaddress
from cortexutils.analyzer import Analyzer


class CIRCLPassiveDNSAnalyzer(Analyzer):
    """The circl.lu passive dns is queried using the PyPDNS module from circl.lu."""
    def __init__(self):
        Analyzer.__init__(self)
        self.pdns = pypdns.PyPDNS(basic_auth=(self.getParam('config.user', None, 'No passiveDNS username given.'),
                                              self.getParam('config.password', None, 'No passiveDNS password given.')))

    def query(self, domain):
        """The actual query happens here. Time from queries is replaced with isoformat.

        :param domain: The domain/url/ip which should gets queried.
        :type domain: str
        :returns: List of dicts containing the search results.
        :rtype: [list, dict]
        """
        result = {}

        try:
            result = self.pdns.query(domain)
        except:
            self.error('Exception while querying passiveDNS. Check the domain/url/ip format.')

        # Clean the datetime problems in order to correct the json serializability
        clean_result = []
        for ind, resultset in enumerate(result):
            if resultset.get('time_first', None):
                resultset['time_first'] = resultset.get('time_first').isoformat(' ')
            if resultset.get('time_last', None):
                resultset['time_last'] = resultset.get('time_last').isoformat(' ')
            clean_result.append(resultset)

        return clean_result

    def summary(self, raw):
        taxonomies = []
        level = "info"
        namespace = "CIRCL"
        predicate = "PassiveDNS"

        if ("results" in raw):
            r = len(raw.get('results'))

        if r == 0 or r == 1:
            value = "\"{} record\"".format(r)
        else:
            value = "\"{} records\"".format(r)

        taxonomies.append(self.build_taxonomy(level, namespace, predicate, value))
        return {"taxonomies": taxonomies}





    def run(self):
        query = ''
        if self.data_type == 'url':
            splittedurl = self.getData().split('/')
            if 'http' in splittedurl[0]:
                query = splittedurl[2]
            else:
                query = splittedurl[0]
        elif self.data_type == 'domain':
            query = self.getData()
            if '/' in query:
                self.error('\'/\' found in the supplied domain. use the URL datatype instead')
        elif self.data_type == 'ip':
            query = self.getData()
            try:
                ip = ipaddress.ip_address(query)
            except:
                self.error('Wrong IPv4 or IPv6 format in the supplied ip. use the URL or Domain datatype instead')
        else:
            self.error('invalid datatype')
        self.report({'results': self.query(query)})

if __name__ == '__main__':
    CIRCLPassiveDNSAnalyzer().run()
