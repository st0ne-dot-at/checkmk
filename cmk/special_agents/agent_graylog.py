#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | "_ \ / _ \/ __| |/ /   | |\/| | " /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2019             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from typing import NamedTuple, Text
import argparse
import time
import json
import sys
import requests

GraylogSection = NamedTuple("GraylogSection", [
    ("name", Text),
    ("uri", Text),
])


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_arguments(argv)

    # calculate time difference from now and args.since in ISO8601 Format
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - args.since))

    # Add new queries here
    sections = [
        GraylogSection(name="alerts", uri="/streams/alerts?limit=300"),
        GraylogSection(name="cluster_health", uri="/system/indexer/cluster/health"),
        GraylogSection(name="cluster_inputstates", uri="/cluster/inputstates"),
        GraylogSection(name="cluster_stats", uri="/system/cluster/stats"),
        GraylogSection(name="cluster_traffic", uri="/system/cluster/traffic?days=1&daily=false"),
        GraylogSection(name="failures", uri="/system/indexer/failures/count/?since=%s" % since),
        GraylogSection(name="jvm", uri="/system/metrics/namespace/jvm.memory.heap"),
        GraylogSection(name="license", uri="/plugins/org.graylog.plugins.license/licenses/status"),
        GraylogSection(name="messages", uri="/count/total"),
        GraylogSection(name="nodes", uri="/cluster"),
        GraylogSection(name="sidecars", uri="/sidecars"),
    ]

    try:
        handle_request(args, sections)
    except Exception:
        if args.debug:
            return 1

    return 0


def handle_request(args, sections):
    url_base = "%s://%s:%s/api" % (args.proto, args.hostname, args.port)

    for section in sections:
        if section.name not in args.sections:
            continue

        url = url_base + section.uri

        value = handle_response(url, args).json()

        # add failure details
        if section.name == "failures":
            url_failures = url_base + "/system/indexer/failures?limit=30"

            value.update(handle_response(url_failures, args).json())

            # add param from datasource for use in check output
            value.update({"ds_param_since": args.since})

        if section.name == "nodes":
            url_nodes = url_base + "/cluster/inputstates"
            node_inputstates = handle_response(url_nodes, args).json()

            node_list = []
            for node in node_inputstates:
                if node in value:
                    value[node].update({"inputstates": node_inputstates[node]})
                    value = {node: value[node]}
                    if args.display_node_details == "node":
                        handle_piggyback(value, args, value[node]["hostname"], section.name)
                        continue
                    node_list.append(value)

                if node_list:
                    handle_output(node_list, section.name, args)

        if section.name == "jvm":
            metric_data = value.get("metrics")
            if metric_data is None:
                continue

            new_value = {}
            for metric in value["metrics"]:

                metric_value = metric.get("metric", {}).get("value")
                metric_name = metric.get("full_name")
                if metric_value is None or metric_name is None:
                    continue

                new_value.update({metric_name: metric_value})

            value = new_value

        if section.name == "sidecars":
            sidecars = value.get("sidecars")
            if sidecars is not None:
                sidecar_list = []
                for sidecar in sidecars:
                    if args.display_sidecar_details == "sidecar":
                        handle_piggyback(sidecar, args, sidecar["node_name"], section.name)
                        continue
                    sidecar_list.append(sidecar)

                if sidecar_list:
                    handle_output(sidecar_list, section.name, args)

        if section.name not in ["nodes", "sidecars"]:
            handle_output(value, section.name, args)


def handle_response(url, args):
    try:
        response = requests.get(url, auth=(args.user, args.password))
    except requests.exceptions.RequestException as e:
        sys.stderr.write("Error: %s\n" % e)
        if args.debug:
            raise

    return response


def handle_output(value, section, args):
    sys.stdout.write("<<<graylog_%s:sep(0)>>>\n" % section)
    if isinstance(value, list):
        for entry in value:
            sys.stdout.write("%s\n" % json.dumps(entry))
        return

    sys.stdout.write("%s\n" % json.dumps(value))

    for name, param_piggyback, value_piggyback in [
        ("nodes", args.display_node_details, "node"),
        ("sidecars", args.display_sidecar_details, "sidecar"),
    ]:
        if section == name and param_piggyback == value_piggyback:
            sys.stdout.write("<<<<>>>>\n")

    return


def handle_piggyback(value, args, piggyback_name, section):
    sys.stdout.write("<<<<%s>>>>\n" % piggyback_name)
    handle_output(value, section, args)
    return


def parse_arguments(argv):
    sections = [
        "alerts", "cluster_stats", "cluster_traffic", "failures", "jvm", "license", "messages",
        "nodes", "sidecars"
    ]

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("-u", "--user", default=None, help="Username for graylog login")
    parser.add_argument("-s", "--password", default=None, help="Password for graylog login")
    parser.add_argument("-P",
                        "--proto",
                        default="https",
                        help="Use 'http' or 'https' for connection to graylog (default=https)")
    parser.add_argument("-p",
                        "--port",
                        default=443,
                        type=int,
                        help="Use alternative port (default: 443)")
    parser.add_argument("-t",
                        "--since",
                        default=1800,
                        type=int,
                        help="The time in seconds, since when failures should be covered")
    parser.add_argument(
        "-m",
        "--sections",
        default=sections,
        help="""Comma seperated list of data to query. Possible values: %s (default: all)""" %
        ", ".join(sections))
    parser.add_argument("--display_node_details",
                        default=None,
                        choices=('host', 'node'),
                        help="""You can optionally choose, where the node details are shown.
        Default is the queried graylog host. Possible values: host, node (default: host)""")
    parser.add_argument("--display_sidecar_details",
                        default="host",
                        choices=('host', 'sidecar'),
                        help="""You can optionally choose, where the sidecar details are shown.
        Default is the queried graylog host. Possible values: host, sidecar (default: host)""")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Debug mode: let Python exceptions come through")

    parser.add_argument("hostname",
                        metavar="HOSTNAME",
                        help="Name of the graylog instance to query.")

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
