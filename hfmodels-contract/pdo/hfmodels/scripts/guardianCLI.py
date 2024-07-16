#!/usr/bin/env python

# Copyright 2024 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Data guardian service.
"""

import os
import sys
import argparse

import signal

import pdo.common.config as pconfig
import pdo.common.logger as plogger
import pdo.common.utility as putils

from pdo.common.wsgi import AppWrapperMiddleware
from pdo.hfmodels.wsgi import wsgi_operation_map
from pdo.hfmodels.common.capability_keystore import CapabilityKeyStore
from pdo.hfmodels.common.endpoint_registry import EndpointRegistry

import logging
logger = logging.getLogger(__name__)


## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
from twisted.web import http
from twisted.web.resource import Resource, NoResource
from twisted.web.server import Site
from twisted.python.threadpool import ThreadPool
from twisted.internet import reactor, defer
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.web.wsgi import WSGIResource

## ----------------------------------------------------------------
def ErrorResponse(request, error_code, msg) :
    """Generate a common error response for broken requests
    """

    result = ""
    if request.method != 'HEAD' :
        result = msg + '\n'
        result = result.encode('utf8')

    request.setResponseCode(error_code)
    request.setHeader(b'Content-Type', b'text/plain')
    request.setHeader(b'Content-Length', len(result))
    request.write(result)

    try :
        request.finish()
    except :
        logger.exception("exception during request finish")
        raise

    return request

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def __shutdown__(*args) :
    logger.warn('shutdown request received')
    reactor.callLater(1, reactor.stop)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def TestService(config) :
    """Test for the existance of a guardian service with the current configuration
    """

    from pdo.service_client.generic import MessageException
    from pdo.hfmodels.common.guardian_service import GuardianServiceClient

    try :
        http_port = config['GuardianService']['HttpPort']
        http_host = config['GuardianService']['Host']
        service_url = 'http://{}:{}'.format(http_host, http_port)
    except KeyError as ke :
        logger.error('missing configuration for %s', str(ke))
        sys.exit(-1)

    try :
        service_client = GuardianServiceClient(service_url)
    except MessageException as m :
        # if the error is a message exception then the message stays as info
        # since the point of this routine is to test and this means the test
        # failed
        logger.info('failed to contact guardian service; {}'.format(str(m)))
        sys.exit(-1)
    except Exception as e :
        # if the exception is something more serious, then show the error
        # message
        logger.error('failed to contact guardian service; {}'.format(str(e)))
        sys.exit(-1)

    logger.info('guardian service running; {}'.format(service_url))
    sys.exit(0)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def StartService(config, capability_keystore, endpoint_registry) :
    try :
        http_port = config['GuardianService']['HttpPort']
        http_host = config['GuardianService']['Host']
        worker_threads = config['GuardianService'].get('WorkerThreads', 8)
        reactor_threads = config['GuardianService'].get('ReactorThreads', 8)
    except KeyError as ke :
        logger.error('missing configuration for %s', str(ke))
        sys.exit(-1)

    logger.info('service started on %s:%s', http_host, http_port)

    thread_pool = ThreadPool(minthreads=1, maxthreads=worker_threads)
    thread_pool.start()
    reactor.addSystemEventTrigger('before', 'shutdown', thread_pool.stop)

    root = Resource()
    for (wsgi_verb, wsgi_app) in wsgi_operation_map.items() :
        logger.info('add handler for %s', wsgi_verb)
        verb = wsgi_verb.encode('utf8')
        app = AppWrapperMiddleware(wsgi_app(config, capability_keystore, endpoint_registry))
        root.putChild(verb, WSGIResource(reactor, thread_pool, app))

    site = Site(root, timeout=60)
    site.displayTracebacks = True

    reactor.suggestThreadPoolSize(reactor_threads)

    signal.signal(signal.SIGQUIT, __shutdown__)
    signal.signal(signal.SIGTERM, __shutdown__)

    endpoint = TCP4ServerEndpoint(reactor, http_port, backlog=32, interface=http_host)
    endpoint.listen(site)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def RunService(capability_keystore, endpoint_registry) :
    @defer.inlineCallbacks
    def shutdown_twisted():
        logger.info("Stopping Twisted")
        yield reactor.callFromThread(reactor.stop)

    reactor.addSystemEventTrigger('before', 'shutdown', shutdown_twisted)

    try :
        reactor.run()
    except ReactorNotRunning:
        logger.warn('shutdown')
    except :
        logger.warn('shutdown')

    capability_keystore.close()
    endpoint_registry.close()
    sys.exit(0)

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def LocalMain(config) :

    # load and initialize the model and service keys
    try :
        logger.debug('initialize the service')

        try :
            keystore_filename = config['Data']['CapabilityKeyStore']
        except KeyError as ke :
            logger.error('missing required configuration; %s', str(ke))
            sys.exit(-1)

        keystore_filename = putils.build_file_name(keystore_filename, extension='db')
        capability_keystore = CapabilityKeyStore(keystore_filename)

        try :
            endpoint_filename = config['Data']['EndpointRegistry']
        except KeyError as ke :
            logger.error('missing required configuration; %s', str(ke))
            sys.exit(-1)

        endpoint_filename = putils.build_file_name(endpoint_filename, extension='db')
        endpoint_registry = EndpointRegistry(endpoint_filename)

    except Exception as e :
        logger.exception('failed to initialize service keys; %s', e)
        sys.exit(-1)

    # set up the handlers for the enclave service
    try :
        StartService(config, capability_keystore, endpoint_registry)
    except Exception as e:
        logger.exception('failed to start the enclave service; %s', e)
        sys.exit(-1)

    # and run the service
    RunService(capability_keystore, endpoint_registry)

## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
## XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# -----------------------------------------------------------------
# -----------------------------------------------------------------
def Main() :
    config_map = pconfig.build_configuration_map()

    # parse out the configuration file first
    conffiles = [ 'guardian_service.toml' ]
    confpaths = [ ".", "./etc", config_map['etc'] ]

    parser = argparse.ArgumentParser()

    # allow for override of bindings in the config map
    parser.add_argument('-b', '--bind', help='Define variables for configuration and script use', nargs=2, action='append')

    parser.add_argument('--config', help='configuration file', nargs = '+')
    parser.add_argument('--config-dir', help='directory to search for configuration files', nargs = '+')

    parser.add_argument('--identity', help='Identity to use for the process', required = True, type = str)

    parser.add_argument('--key-dir', help='Directories to search for key files', nargs='+')
    parser.add_argument('--data-dir', help='Path for storing generated files', type=str)

    parser.add_argument('--logfile', help='Name of the log file, __screen__ for standard output', type=str)
    parser.add_argument('--loglevel', help='Logging level', type=str)

    parser.add_argument('--http', help='Port on which to run the http server', type=int)
    parser.add_argument('--block-store', help='Name of the file where blocks are stored', type=str)

    parser.add_argument('--test', help='Test for guardian service', action='store_true')

    options = parser.parse_args()

    # first process the options necessary to load the default configuration
    if options.config :
        conffiles = options.config

    if options.config_dir :
        confpaths = options.config_dir

    config_map['identity'] = options.identity
    if options.data_dir :
        config_map['data'] = options.data_dir

    # set up the configuration mapping from the parameters
    if options.bind :
        for (k, v) in options.bind : config_map[k] = v

    # parse the configuration files
    try :
        config = pconfig.parse_configuration_files(conffiles, confpaths, config_map)
    except pconfig.ConfigurationException as e :
        logger.error(str(e))
        sys.exit(-1)

    # set up the logging configuration
    if config.get('Logging') is None :
        config['Logging'] = {
            'LogFile' : '__screen__',
            'LogLevel' : 'INFO'
        }
    if options.logfile :
        config['Logging']['LogFile'] = options.logfile
    if options.loglevel :
        config['Logging']['LogLevel'] = options.loglevel.upper()

    # make the configuration available to all of the PDO modules
    pconfig.initialize_shared_configuration(config)

    plogger.setup_loggers(config.get('Logging', {}))
    sys.stdout = plogger.stream_to_logger(logging.getLogger('STDOUT'), logging.DEBUG)
    sys.stderr = plogger.stream_to_logger(logging.getLogger('STDERR'), logging.WARN)

    # set up the key search paths
    if config.get('Key') is None :
        config['Key'] = {
            'SearchPath' : [ '.', './keys', config_map['keys'] ],
            'FileName' : options.identity + ".pem"
        }
    if options.key_dir :
        config['Key']['SearchPath'] = options.key_dir

    # set up the enclave service configuration
    if config.get('GuardianService') is None :
        config['GuardianService'] = {
            'HttpPort' : 7101,
            'Host' : 'localhost',
            'Identity' : options.identity,
        }
    if options.http :
        config['GuardianService']['HttpPort'] = options.http

    # GO!
    if options.test :
        TestService(config)
    else :
        LocalMain(config)

## -----------------------------------------------------------------
## Entry points
## -----------------------------------------------------------------
Main()
