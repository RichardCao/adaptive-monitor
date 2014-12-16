#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

import json
import logging

from webob import Response, request
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.lib import dpid as dpid_lib

import adaptivemonitor
import utils


simple_switch_instance_name = 'simple_switch_api_app'
url = '/simpleswitch/mactable/{dpid}'
SWITCHID_PATTERN = dpid_lib.DPID_PATTERN + r'|all'

class SimpleSwitchRest(adaptivemonitor.AdaptiveMonitor):

    _CONTEXTS = {'wsgi' : WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitchRest, self).__init__(*args, **kwargs)
###        self.switches = {}
        wsgi = kwargs['wsgi']
        wsgi.register(SimpleSwitchController, {simple_switch_instance_name : self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(SimpleSwitchRest, self).switch_features_handler(ev)

    def set_mac_to_port(self, datapathid, entry):
        mac_table = self.mac_to_port.setdefault(datapathid, {})
        datapath = self.datapath_list[datapathid]
        entry_port = entry['port']
        entry_mac = entry['mac']
        
        if datapath is not None:
            parser = datapath.ofproto_parser
            if not entry_port in mac_table.values():
                for mac, port in mac_table.items():
                    # from known device to new device
                    actions = [parser.OFPActionOutput(entry_port)]
                    match = parser.OFPMatch(in_port=port, eth_dst=entry_mac)
                    self.add_flow(datapath, 1, match, actions)
                    # from new device to known device
                    actions = [parser.OFPActionOutput(port)]
                    match = parser.OFPMatch(in_port=entry_port, eth_dst=mac)
                    self.add_flow(datapath, 1, match, actions)
                mac_table.update({entry_mac : entry_port})
        return mac_table

class SimpleSwitchController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(SimpleSwitchController, self).__init__(req, link, data, **config)
        self.simple_switch_spp = data[simple_switch_instance_name]
        print "ssc_init\n"
        print self.simple_switch_spp.mac_to_port
        print 6790874762851226928 in self.simple_switch_spp.mac_to_port
        print "\nssc_init_end\n"

    @route('simpleswitch', url, methods=['GET'], requirements={'datapathid': SWITCHID_PATTERN})
    def list_mac_table(self, req, **kwargs):
        
        print "aaa"
        simple_switch = self.simple_switch_spp
     ###   datapathid = dpid.str_to_dpid(kwargs['dpid'])
        print "list"
        print simple_switch
        print "list_mac_table"
        print "\n"
###        if datapathid not in simple_switch.mac_to_port:
###            return Response(status=404)

  ###      mac_table = simple_switch.mac_to_port.get(datapathid, {})
        print "list_mac_table"
        print "\n"
     ###   body = json.dumps(mac_table)
        print "\n"
   ###     return Response(content_type='application/json', body=body)

    @route('simpleswitch', url, methods=['PUT'], requirements={'dpid': SWITCHID_PATTERN})
    def put_mac_table(self, req, **kwargs):
        print "bbb"
        simple_switch = self.simple_switch_spp
        datapathid = dpid_lib.str_to_dpid(kwargs['dpid'])
        print "\ndpid = "
        print datapathid
        print "\n"
        new_entry = eval(req.body)
        print "put"
        print simple_switch.mac_to_port

        print "list_mac_table"
        print self.mac_to_port[datapathid]
        print "\n"

        if datapathid not in simple_switch.mac_to_port:
            return Response(status=404)

        try:
            mac_table = simple_switch.set_mac_to_port(datapathid, new_entry)
            print "put_mac_table"
            print mac_table
            print "\n"
            body = json.dumps(mac_table)
            print body
            print "\n"
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)