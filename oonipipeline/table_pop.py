#!/usr/bin/env python

import os

from glom import glom
from oonipipeline.ooni_datagrabber import OoniDataGrabber
from oonipipeline.ooni_dataparser import OoniDataParser
from oonipipeline.models.models import Status

ooni_grab = OoniDataGrabber()
ooni_parse = OoniDataParser()


def webconn_pop(report_textnames, webconn_model, url, db, new_set, testkeys_model, dns_model, http_request_model,
                control_tcp_model, queries_model, answers_model, requests_model, tcp_model):
    for i in range(len(report_textnames)):
        ooni_grab.download_s3_file(report_textnames[i])
        file_name = report_textnames[i].replace(report_textnames[i][0:11], "")
        useful_json = ooni_parse.webconn_parse(url, file_name, report_textnames[i])  # list of json

        status = Status(
            current=i,
            total=len(report_textnames),
            report_file=report_textnames[i]
        )

        db.session.add(status)
        db.session.commit()

        for j in range(len(useful_json)):
            webconn = webconn_model(
                meta_table=new_set,
                tested_url=glom(useful_json[j], 'tested_url'),
                country=glom(useful_json[j], 'country'),
                asn=glom(useful_json[j], 'asn'),
                test_date=glom(useful_json[j], 'test_date'),
                test_version=glom(useful_json[j], 'test_version'),
                download_link=glom(useful_json[j], 'download_link')
            )
            db.session.add(webconn)
            db.session.commit()
            testkeys = testkeys_model(
                web_connectivity=webconn,
                accessible=glom(useful_json[j], 'test_keys.accessible', default=None),
                blocking=glom(useful_json[j], 'test_keys.blocking', default=None),
                body_length_match=glom(useful_json[j], 'test_keys.body_length_match', default='error'),
                client_resolver=glom(useful_json[j], 'test_keys.client_resolver', default='error'),
                control_failure=glom(useful_json[j], 'test_keys.control_failure', default='error'),
                dns_consistency=glom(useful_json[j], 'test_keys.dns_consistency', default='error'),
                headers_match=glom(useful_json[j], 'test_keys.headers_match', default=None),
                http_experiment_failure=glom(useful_json[j], 'test_keys.http_experiment_failure', default='error'),
                status_code_match=glom(useful_json[j], 'test_keys.status_code_match', default=None),
                title_match=glom(useful_json[j], 'test_keys.title_match', default=None)
            )
            db.session.add(testkeys)
            db.session.commit()
            control_dns = dns_model(
                web_test_keys=testkeys,
                address=glom(useful_json[j], 'test_keys.control.dns.addrs', default='error'),
                failure=glom(useful_json[j], 'test_keys.control.dns.failure', default='error')
            )
            db.session.add(control_dns)
            db.session.commit()
            control_http = http_request_model(
                web_test_keys=testkeys,
                body_length=glom(useful_json[j], 'test_keys.control.http_request.body_length', default=None),
                failure=glom(useful_json[j], 'test_keys.control.http_request.failure', default='error'),
                headers=glom(useful_json[j], 'test_keys.control.http_request.headers', default='error'),
                status_code=glom(useful_json[j], 'test_keys.control.http_request.status_code', default=None),
                title=glom(useful_json[j], 'test_keys.control.http_request.title', default='error')
            )
            db.session.add(control_http)
            db.session.commit()

            for key, value in glom(useful_json[j], 'test_keys.control.tcp_connect', default={}).items():
                control_tcp = control_tcp_model(
                    web_test_keys=testkeys,
                    address=key,
                    result=value
                )
                db.session.add(control_tcp)
                db.session.commit()

            try:
                queries_test_key = useful_json[j]['test_keys']['queries']
                if queries_test_key:  # accommodate for when list is empty
                    queries = queries_model(
                        web_test_keys=testkeys,
                        failure=glom(queries_test_key[0], 'failure', default='error'),
                        hostname=glom(queries_test_key[0], 'hostname', default='error'),
                        query_type=glom(queries_test_key[0], 'query_type', default='error'),
                        resolver_hostname=glom(queries_test_key[0], 'resolver_hostname', default='error'),
                        resolver_port=glom(queries_test_key[0], 'resolver_port', default='error')
                    )
                    db.session.add(queries)
                    db.session.commit()

                    glom_answer = glom(useful_json[j], ('test_keys.queries', ['answers']), default='error')
                    for l in range(len(glom_answer[0])):
                        ans = answers_model(
                            web_queries=queries,
                            answer_type=glom(glom_answer[0][l], 'answer_type', default='error'),
                            ipv4=glom(glom_answer[0][l], 'ipv4', default='error'),
                            ttl=glom(glom_answer[0][l], 'ttl', default='none')
                        )
                        db.session.add(ans)
                        db.session.commit()
            except KeyError:
                pass

            try:
                requests_test_key = useful_json[j]['test_keys']['requests']
                if requests_test_key and requests_test_key != " ":
                    response_body = glom(requests_test_key[0], 'response.body', default=None)
                    if response_body:
                        if isinstance(response_body, dict):
                            response_body = "error"
                        else:
                            response_body = response_body.replace('\n', '').replace('\r', '')
                else:
                    response_body = "error"
                if requests_test_key:
                    requests = requests_model(
                        web_test_keys=testkeys,
                        failure=glom(requests_test_key[0], 'failure', default='error'),
                        request_headers=glom(requests_test_key[0], 'request.headers', default='error'),
                        request_method=glom(requests_test_key[0], 'request.method', default='error'),
                        request_url=glom(requests_test_key[0], 'request.url', default='error'),
                        response_code=glom(requests_test_key[0], 'response.code', default=None),
                        response_headers=glom(requests_test_key[0], 'response.headers', default=None),
                        response_body=response_body
                    )
                    try:
                        db.session.add(requests)
                        db.session.commit()
                    except ValueError:
                        db.session.rollback()

            except KeyError:
                pass

            for m in range(len(glom(useful_json[j], 'test_keys.tcp_connect', default='error'))):
                tcp = tcp_model(
                    web_test_keys=testkeys,
                    ip=glom(useful_json[j]['test_keys']['tcp_connect'][m], 'ip', default='error'),
                    port=glom(useful_json[j]['test_keys']['tcp_connect'][m], 'port', default='error'),
                    blocked=glom(useful_json[j]['test_keys']['tcp_connect'][m]['status'], 'blocked', default='error'),
                    failure=glom(useful_json[j]['test_keys']['tcp_connect'][m]['status'], 'failure', default='error'),
                    success=glom(useful_json[j]['test_keys']['tcp_connect'][m]['status'], 'success', default='error')
                )
                db.session.add(tcp)
                db.session.commit()

        os.remove(file_name)

    Status.query.delete()
    db.session.commit()


def dns_consistency_pop(report_textnames, dns_model, testkeys_model, errors_model, failed_model, inconsistent_model,
                        queries_model, answers_model, url, db, new_set):
    for i in range(len(report_textnames)):
        ooni_grab.download_s3_file(report_textnames[i])
        file_name = report_textnames[i].replace(report_textnames[i][0:11], "")
        useful_json = ooni_parse.dns_parse(url, file_name, report_textnames[i])

        status = Status(
            current=i,
            total=len(report_textnames),
            report_file=report_textnames[i]
        )

        db.session.add(status)
        db.session.commit()

        for j in range(len(useful_json)):
            dns_cons = dns_model(
                meta_table=new_set,
                input=glom(useful_json[j], 'input'),
                country=glom(useful_json[j], 'country'),
                asn=glom(useful_json[j], 'asn'),
                test_date=glom(useful_json[j], 'test_date'),
                test_name=glom(useful_json[j], 'test_name'),
                test_version=glom(useful_json[j], 'test_version'),
                download_link=glom(useful_json[j], 'download_link')
            )
            db.session.add(dns_cons)
            db.session.commit()

            testkeys = testkeys_model(
                dns_consistency=dns_cons,
                success_rate=glom(useful_json[j], 'success_rate'),
                inconsistent_rate=glom(useful_json[j], 'inconsistent_rate'),
            )
            db.session.add(testkeys)
            db.session.commit()
            for key, value in useful_json[j]['errors'].items():
                errors = errors_model(
                    test_keys=testkeys,
                    resolver_ip=key,
                    error_string=value,
                )
                db.session.add(errors)
                db.session.commit()
            for m in range(len(useful_json[j]['failed_addresses'])):
                failed = failed_model(
                    test_keys=testkeys,
                    address=useful_json[j]['failed_addresses'][m]
                )
                db.session.add(failed)
                db.session.commit()
            for n in range(len(useful_json[j]['inconsistent_addresses'])):
                inconsistent = inconsistent_model(
                    test_keys=testkeys,
                    address=useful_json[j]['inconsistent_addresses'][n]
                )
                db.session.add(inconsistent)
                db.session.commit()

            for k in range(len(useful_json[j]['hostname'])):
                queries = queries_model(
                    test_keys=testkeys,
                    failure=useful_json[j]['failure'][k],
                    hostname=useful_json[j]['hostname'][k],
                    query_type=useful_json[j]['query_type'][k],
                    resolver_hostname=useful_json[j]['resolver_hostname'][k],
                    resolver_port=useful_json[j]['resolver_port'][k]
                )
                db.session.add(queries)
                db.session.commit()

                for l in range(len(useful_json[j]['answers'][k])):
                    ans = answers_model(
                        dns_queries=queries,
                        answer_type=glom(useful_json[j]['answers'][k][l], 'answer_type', default=None),
                        ipv4=glom(useful_json[j]['answers'][k][l], 'ipv4', default=None),
                        ttl=glom(useful_json[j]['answers'][k][l], 'ttl', default=None)
                    )
                    db.session.add(ans)
                    db.session.commit()
        os.remove(file_name)

    Status.query.delete()
    db.session.commit()


def whats_app(report_textnames, models, db, new_set):
    return ""
