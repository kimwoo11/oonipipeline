#!/usr/bin/env python

import json
from glom import glom


class OoniDataParser:

    @staticmethod
    def download_url(textname):
        """
        Given a report textname give a URL where the json file can be downloaded.
        :param textname:
        :return: download link
        """
        base_url = "https://api.ooni.io/files/download/"
        return base_url + textname

    @staticmethod
    def get_json_for_url_in_file(given_url, json_file):
        fail = None
        try:
            f = open(json_file)
        except IOError:
            return fail

        for data in f.readlines():
            this_json = json.loads(data)
            if "input" in this_json:
                if this_json["input"] is None:
                    continue
                elif given_url in this_json["input"]:
                    f.close()
                    return this_json

    @staticmethod
    def get_json_from_file(json_file):
        fail = None
        try:
            f = open(json_file)
        except IOError:
            return fail

        json_list = []  # list of json
        for data in f.readlines():
            json_list.append(json.loads(data))
        f.close()
        return json_list

    def webconn_parse(self, given_url, json_input, textname):
        if given_url is None:
            full_list = self.get_json_from_file(json_input)
        else:
            full_list = []
            temp_list = self.get_json_for_url_in_file(given_url, json_input)
            full_list.append(temp_list)

        useful_list = []
        for row in full_list:
            useful_list.append({
                "tested_url": glom(row, 'input', default='error'),
                "country": glom(row, 'probe_cc', default='error'),
                "asn": glom(row, 'probe_asn', default='error'),
                "test_date": glom(row, 'test_start_time', default='error'),
                "test_version": glom(row, 'test_version', default='error'),
                "download_link": self.download_url(textname),
                "test_keys": glom(row, 'test_keys', default='error')
            })

        return useful_list

    def dns_parse(self, given_url, json_input, textname):
        if given_url is None:
            full_list = self.get_json_from_file(json_input)
        else:
            full_list = []
            temp_list = self.get_json_for_url_in_file(given_url, json_input)
            full_list.append(temp_list)
        useful_list = []
        for row in full_list:
            useful_list.append({
                # DnsConsistency
                "input": glom(row, 'input', default='error'),
                "country": glom(row, 'probe_cc', default='error'),
                "test_date": glom(row, 'test_start_time', default='error'),
                "test_name": glom(row, 'test_name', default='error'),
                "test_version": glom(row, 'test_version', default='error'),
                "asn": glom(row, 'probe_asn', default='error'),

                # DnsTestKeys
                "success_rate": str(len(glom(row, 'test_keys.successful')))+"/"+str(len(glom(row, 'test_keys.errors'))),
                "inconsistent_rate": str(len(glom(row, 'test_keys.inconsistent'))) + "/" +
                                     str(len(glom(row, 'test_keys.errors'))),  # contains all addresses

                # Errors
                "errors": glom(row, 'test_keys.errors', default='error'),

                # Failed
                "failed_addresses": glom(row, 'test_keys.failed', default='error'),

                # Inconsistent
                "inconsistent_addresses": glom(row, 'test_keys.inconsistent', default='error'),

                # DnsQueries and DnsAnswers
                "failure": glom(row, ('test_keys.queries', ['failure']), default='error'),
                "hostname": glom(row, ('test_keys.queries', ['hostname']), default='error'),
                "query_type": glom(row, ('test_keys.queries', ['query_type']), default='error'),
                "resolver_hostname": glom(row, ('test_keys.queries', ['resolver_hostname']), default='error'),
                "resolver_port": glom(row, ('test_keys.queries', ['resolver_port']), default='error'),
                "answers": glom(row, ('test_keys.queries', ['answers']), default='error'),
                "download_link": self.download_url(textname)
            })

        return useful_list
