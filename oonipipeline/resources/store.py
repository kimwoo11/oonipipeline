from oonipipeline import table_pop
from flask import request
from flask_restful import Resource
from oonipipeline.models.models import (DnsConsistency, DnsQueries, DnsAnswers, DnsTestKeys, Failed, Inconsistent,
                                 Errors, Webconn, WebTestKeys, ControlDns, ControlHttpRequest, ControlTcpConnect,
                                 WebQueries, WebAnswers, TcpConnect, Requests, MetaTable, MetaTableSchema, db,
                                 meta, metadb_session, StorePostSchema)


class StoreResource(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'status': 'error', 'message': 'No input data provided'}, 400

        # --- API Parameters --- #
        set_name = json_data.get('set_name', None)  # Required
        country = json_data.get('country', None)  # Not Required
        asn = json_data.get('asn', None)  # Not Required
        url = json_data.get('url', None)  # Not Required
        start = json_data.get('start_date', None)  # Required
        end = json_data.get('end_date', None)  # Required
        comment = json_data.get('comment', None)  # Not Required
        test_name = json_data.get('test_name', None)  # Required

        if (test_name == "web_connectivity") or (test_name == "dns_consistency"):
            pass
        else:
            return {'status': 'error', 'message': 'Please provide a valid test name'}, 400

        # --- Deserialize and validate input --- #
        data, errors = StorePostSchema().load(json_data)
        if errors:
            return {'status': 'error', 'message': errors}, 422

        data_set = MetaTable.query.filter_by(set_name=set_name).first()
        if data_set:
            return {'status': 'error', 'message': 'The specified data set name is already taken'}, 400

        # Add flexibility to asn and country input:
        if asn:
            if not asn[0].isalpha():
                asn = 'AS' + asn
            else:
                asn = list(asn)
                for i in range(len(asn)):
                    if asn[i].isalpha():
                        if asn[i].islower():
                            asn[i] = asn[i].upper()
                asn = "".join(asn)

        if country:
            country = list(country)
            for i in range(len(country)):
                if country[i].islower():
                    country[i] = country[i].upper()
            country = ''.join(country)

        # --- Record new set into Meta Table --- #
        new_set = MetaTable(
            set_name=set_name,
            test_name=test_name,
            comment=comment
        )
        # --- Connecting Tables --- # (from metadb)
        input_t = meta.tables['input']
        measurement_t = meta.tables['measurement']
        report_t = meta.tables['report']

        # Query results summary
        input_query = []  # input_query[i] = (input_no, report_no); from "measurement" table
        report_textnames = []  # Stores the text name (can download from s3 with this)
        shared_report_no = []  # Stores the report_no of reports that have data about the specified url

        # Accounting for all cases for API parameter inputs
        '''
        ___All Cases___:
        Case 1: (country and asn and url) is None
        Case 2: only (country and asn) is None
        Case 3: only (country and url) is None
        Case 4: only (url and asn) is None
        Case 5: only country is None
        Case 6: only asn is None
        Case 7: only url is None
        Case 8: nothing is None
        '''
        # report_query[i] = (report_no, textname); from "report" table
        if (country or asn or url) is None or (country or asn) is None:  # Case 1 and Case 2
            report_query = metadb_session.query(report_t.c.report_no, report_t.c.textname) \
                .filter(report_t.c.test_name == test_name,
                        report_t.c.test_start_time >= start,
                        report_t.c.test_start_time <= end).all()
        elif asn is not None:  # Case 3 and Case 5
            report_query = metadb_session.query(report_t.c.report_no, report_t.c.textname) \
                .filter(report_t.c.test_name == test_name,
                        report_t.c.probe_asn == asn,
                        report_t.c.test_start_time >= start,
                        report_t.c.test_start_time <= end).all()
        elif (url or asn) is None or asn is None:  # Case 4 and Case 6
            report_query = metadb_session.query(report_t.c.report_no, report_t.c.textname) \
                .filter(report_t.c.test_name == test_name,
                        report_t.c.probe_cc == country,
                        report_t.c.test_start_time >= start,
                        report_t.c.test_start_time <= end).all()
        else:  # Case 7 and Case 8
            report_query = metadb_session.query(report_t.c.report_no, report_t.c.textname) \
                .filter(report_t.c.test_name == test_name,
                        report_t.c.probe_asn == asn,
                        report_t.c.probe_cc == country,
                        report_t.c.test_start_time >= start,
                        report_t.c.test_start_time <= end).all()

        if url is not None:  # Populates for Case 2, Case 5, Case 6, Case 8
            if report_query:
                for row in report_query:
                    query = metadb_session.query(measurement_t.c.input_no, measurement_t.c.report_no) \
                        .filter(measurement_t.c.report_no == row[0]).all()
                    for num in query:
                        input_query.append(num)
            else:
                return {'status': 'error', 'message': 'No data found that fits given specifications'}, 400
            # url_query[i] = (input_no, url); from "input" table
            url_query = metadb_session.query(input_t.c.input_no, input_t.c.input).filter(input_t.c.input == url).first()
            if url_query is None:
                return {'status': 'error', 'message': 'The specified URL does not exist or has not been tested'}, 400
            else:
                for row in input_query:
                    if row[0] == url_query[0]:
                        shared_report_no.append(row[1])

            for row in report_query:
                for index in range(len(shared_report_no)):
                    if row[0] == shared_report_no[index]:
                        report_textnames.append(row[1])

            if test_name == "web_connectivity":
                table_pop.webconn_pop(report_textnames, Webconn, url, db, new_set, WebTestKeys, ControlDns,
                                      ControlHttpRequest, ControlTcpConnect, WebQueries, WebAnswers, Requests,
                                      TcpConnect)
            elif test_name == "dns_consistency":
                table_pop.dns_consistency_pop(report_textnames, DnsConsistency, DnsTestKeys, Errors, Failed,
                                              Inconsistent, DnsQueries, DnsAnswers, url, db, new_set)

            elif test_name == "whatsapp":
                ""

        if url is None:  # Populates for Case 1, Case 3, Case 4, Case 7
            if report_query:
                for row in report_query:
                    report_textnames.append(row[1])

                if test_name == "web_connectivity":
                    table_pop.webconn_pop(report_textnames, Webconn, url, db, new_set, WebTestKeys, ControlDns,
                                          ControlHttpRequest, ControlTcpConnect, WebQueries, WebAnswers, Requests,
                                          TcpConnect)
                elif test_name == "dns_consistency":
                    table_pop.dns_consistency_pop(report_textnames, DnsConsistency, DnsTestKeys, Errors, Failed,
                                                  Inconsistent, DnsQueries, DnsAnswers, url, db, new_set)

                elif test_name == "whatsapp":
                    ""
            else:
                return {'status': 'error', 'message': 'No data found that fits given specifications'}, 400

        db.session.add(new_set)
        db.session.commit()

        result = MetaTableSchema().dump(new_set).data

        return {"status": 'success', 'new_set': result}, 201
