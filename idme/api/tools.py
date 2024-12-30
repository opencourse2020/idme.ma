#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: myrthings
"""

import datetime as dt
import hmac
import hashlib
from base64 import b64encode
import difflib
from ipware import get_client_ip

def period_7d(date):
    x=dt.date.isocalendar(date)
    return str(x[0])+'-w{:02d}'.format(x[1])

def period_28d(date):
    x=dt.date.isocalendar(date)
    return str(x[0])+'-28d-'+str(x[1]//4+1)


def period_w(date):
    x=date.strftime("%Y-%m/%d").split('/')
    day=date.day
    if day<8:
        return x[0]+'-'+'w1'
    elif day<15:
        return x[0]+'-'+'w2'
    elif day<22:
        return x[0]+'-'+'w3'
    elif day<28:
        return x[0]+'-'+'w4'
    else:
        return x[0]+'-'+'w5'
    
def period_q(date):
    x=date.strftime("%Y/%m").split('/')
    month=date.month
    if month<4:
        return x[0]+'-'+'q1'
    elif month<7:
        return x[0]+'-'+'q2'
    elif month<10:
        return x[0]+'-'+'q3'
    else:
        return x[0]+'-'+'q4'

def period_d(date):
    return date.strftime("%Y-%m-%d")

def period_m(date):
    return date.strftime("%Y-%m")

def custom_period(tipo,date):
    if tipo=='7d':
        return period_7d(date)
    elif tipo=='28d':
        return period_28d(date)
    elif tipo=='w':
        return period_w(date)
    elif tipo=='m':
        return period_m(date)
    elif tipo=='d':
        return period_d(date)
    elif tipo=='q':
        return period_q(date)
    
    
def custom_representative(tipo, date): #date not datetime
    if tipo=='7d':
        iso=dt.date.isocalendar(date)
        return dt.datetime.strptime('{:04d} {:02d} 1'.format(iso[0],iso[1]), '%G %V %u').date()
    elif tipo=='28d':
        iso=dt.date.isocalendar(date)
        return dt.datetime.strptime('{:04d} {:02d} 1'.format(iso[0],iso[1]//4*4 if iso[1]//4!=0 else 1), '%G %V %u').date()
    elif tipo=='m':
        return dt.date(date.year,date.month,1)
    elif tipo=='d':
        return date
    elif tipo=='q':
        return dt.date(date.year,date.month//3*3 if date.month//3!=0 else 1,1)


def verifySignature(receivedSignature: str, secret, params):

  data = "-".join(params)
  data = data.encode('utf-8')
  computed_sig = hmac.new(secret.encode('utf-8'), msg=data, digestmod=hashlib.sha256).digest()
  signature = b64encode(computed_sig).decode()
  if signature == receivedSignature:
    return True
  return False


def check_name(name, fname, lname):
    name_str = name.lower().split()

    similar = difflib.get_close_matches(fname, name_str)
    # similar = []
    if len(similar) > 0:
        fname_status = True
    else:
        fname_status = False

    similar = difflib.get_close_matches(lname, name_str)
    if len(similar) > 0:
        lname_status = True
    else:
        lname_status = False

    if fname_status and lname_status:
        return True


def check_ip(request):
    client_ip, is_routable = get_client_ip(request, request_header_order=['X_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'])
    if client_ip and is_routable:
        return client_ip
    else:
        return None

