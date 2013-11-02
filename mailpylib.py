#!/usr/bin/python
# -*- coding: utf-8 -*-

"""mailpylib.py

Author: Lucas Pimentel Lellis (lucaslellis [at] gmail [dot] com)
Description: A small library to make it easier to
             send emails with python.

Copyright 2013 Lucas Pimentel Lellis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from email import Encoders
import os
import smtplib
import socket

from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def process_attachments(attachments_list):
    parts = []
    if attachments_list:
        for filename in attachments_list:
            try:
                attached_file = open(filename, 'rb')
                part = MIMEBase('application', "octet-stream")
                part.set_payload(attached_file.read())
                Encoders.encode_base64(part)
                attachment = 'attachment; filename="%s"' % os.path.basename(filename)
                part.add_header('Content-Disposition', attachment)
                parts.append(part)
            except IOError, e:
                print "WARNING: Error reading attachment file - %s" % e
    return parts


def sendmail(body, sender, recipients_list, mta, subject, attachments_list, html=False):
    """
        Ref: http://mg.pov.lt/blog/unicode-emails-in-python.html
             http://code.activestate.com/recipes/473810/
    """

    body_charset = ""
    for body_charset in "US-ASCII", "ISO-8859-1", "UTF-8":
        try:
            body.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break

    message_root = MIMEMultipart("related")
    message_root["From"] = sender.encode("ascii")
    message_root["To"] = ",".join(recipients_list).encode("ascii")
    for subject_charset in "US-ASCII", "ISO-8859-1", "UTF-8":
        try:
            message_root["Subject"] = subject.decode(subject_charset)
        except UnicodeError:
            pass
        else:
            break

    message_altern = MIMEMultipart("alternative")
    message_altern.attach(MIMEText(body, "plain", body_charset))
    if html:
        message_altern.attach(MIMEText(body, "html", body_charset))

    message_root.attach(message_altern)

    for part in process_attachments(attachments_list):
        message_root.attach(part)

    try:
        smtp_obj = smtplib.SMTP(mta)
        smtp_obj.sendmail(sender, recipients_list, message_root.as_string())
        smtp_obj.quit()
        return 0
    except smtplib.SMTPException, e:
        print "ERROR sending email: %s" % e
        return 1
    except socket.error, e:
        print "ERROR sending email: %s" % e
        return 1
