# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import base64
import os

import cli_common.taskcluster
import tooltool_api.config

DEBUG = bool(os.environ.get('DEBUG', False))


# -- LOAD SECRETS -------------------------------------------------------------

required = [
    'APP_CHANNEL',
    'SECRET_KEY_BASE64',
    'DATABASE_URL',
    # https://github.com/mozilla/build-cloud-tools/blob/master/configs/cloudformation/tooltool.py
    'S3_REGIONS',
    # https://github.com/mozilla/build-cloud-tools/blob/master/configs/cloudformation/iam_relengapi.py
    'S3_REGIONS_ACCESS_KEY_ID',
    'S3_REGIONS_SECRET_ACCESS_KEY',
    'PULSE_USER',
    'PULSE_PASSWORD',
]

existing = {x: os.environ.get(x) for x in required if x in os.environ}
existing['ALLOW_ANONYMOUS_PUBLIC_DOWNLOAD'] = False
# This value should be fairly short (and its value is included in the
# `upload_batch` docstring).  Uploads cannot be validated until this
# time has elapsed, otherwise a malicious uploader could alter a file
# after it had been verified.
existing['UPLOAD_EXPIRES_IN'] = 60
existing['DOWLOAD_EXPIRES_IN'] = 60

secrets = cli_common.taskcluster.get_secrets(
    os.environ.get('TASKCLUSTER_SECRET'),
    tooltool_api.config.PROJECT_NAME,
    required=required,
    existing=existing,
    taskcluster_client_id=os.environ.get('TASKCLUSTER_CLIENT_ID'),
    taskcluster_access_token=os.environ.get('TASKCLUSTER_ACCESS_TOKEN'),
)

locals().update(secrets)

RELENGAPI_AUTH = True
SECRET_KEY = base64.b64decode(secrets['SECRET_KEY_BASE64'])


# -- DATABASE -----------------------------------------------------------------

SQLALCHEMY_TRACK_MODIFICATIONS = False

if DEBUG:
    SQLALCHEMY_ECHO = True

# We require DATABASE_URL set by environment variables for branches deployed to Dockerflow.
if 'DATABASE_URL' not in os.environ:
    raise RuntimeError(f'DATABASE_URL has to be set as an environment variable, when '
                       f'APP_CHANNEL is set to {secrets["APP_CHANNEL"]}')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
