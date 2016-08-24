#
# Project Ginger S390x
#
# Copyright IBM, Corp. 2015
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import ConfigParser
import os
import subprocess
import time

DASD_CONF = '/etc/dasd.conf'
ZFCP_CONF = '/etc/zfcp.conf'

ifcfg_path = '/etc/sysconfig/network-scripts/ifcfg-enccw<deviceid>'
ifcfg_content = "DEVICE=enccw<deviceid>\n" \
                "TYPE=Ethernet\n" \
                "ONBOOT=yes\n" \
                "NETTYPE=qeth\n" \
                "SUBCHANNELS=<subchannels>"

def readconfig(session, configfile, section, key):
    session.logging.info(
        '-->utils.readconfig(): configfile:%s, section:%s, key:%s' % (configfile, section, key))

    if configfile:
        try:
            session.logging.info('Reading configuration file %s' % configfile)
            params = ConfigParser.ConfigParser()
            params.read(configfile)
        except Exception as e:
            session.logging.error("Failed to read config file %s. Error: %s" % (configfile, e.__str__()))
            session.logging.info('<-- utils.readconfig()')
            return
        if params.has_section(section):
            if params.has_option(section, key):
                value = params.get(section, key)
                session.logging.info('<-- utils.readconfig()')
                return value
            else:
                session.logging.error("Option %s is not avaliable in Section %s of config file %s" % (key, section, configfile))
        else:
            session.logging.error("Section %s is not available in the config file %s" % (section, configfile))
    else:
        session.logging.error('Configuration file required')

    session.logging.info('<-- utils.readconfig()')


def wait_task_status_change(session, task_id, task_uri='/plugins/gingers390x/tasks/', task_final_status='finished',
                            task_current_status='running'):
    """
    Wait till task changed its status from task current status
    :param session: session for logging into restful api of the kimchi
    :param task_id: Task Id for which status need to be checked
    :param task_final_status: Final expected status of task
    :param task_current_status: Current status of task
    :return:task_resp: Get response of task id, if task status is other than task_final_status or task_current_status, Raise exception
    """
    session.logging.info(
        '-->utils.wait_task_status_change(): task_id:%s |task_uri:%s |task_final_status:%s |task_current_status:%s'
        %(str(task_id), task_uri, task_final_status, task_current_status))
    counter = 0

    while True:
        if counter > 10:
            raise Exception('Task status change timed out for task id: %s' % str(task_id))

        counter += 1

        task_resp = session.request_get_json(
            task_uri + '/' + task_id)
        task_status = task_resp["status"]
        if task_status == task_current_status:
            time.sleep(2)
            continue
        elif task_status == task_final_status:
            break
        else:
            raise Exception('Task status does not changed to %s. Task Response:%s' % (task_final_status, task_resp))

    session.logging.debug('task_resp:%s' % task_resp)
    session.logging.info('<--utils.wait_task_status_change()')
    return task_resp


def addto_ignore_list(session, ignored_devices):
    session.logging.info('-->utils.addto_ignore_list(): devices :%s' % ignored_devices)
    added_devices = ignored_devices
    for device in ignored_devices:
        device = str(device)
        cmd = ['cio_ignore', '-a', device]
        out, error, rc = run_command(session, cmd)
        if rc:
            session.logging.info('failed to add device "%s" to ignore list.'
                                 ' Error: %s' % (device, error))
            added_devices.remove(device)
    session.logging.info('<--utils.addto_ignore_list()')
    return added_devices


def remove_from_ignore_list(session, remove_devices):
    session.logging.info('-->utils.remove_from_ignore_list(): devices :%s' % remove_devices)
    failed_devices = []
    for device in remove_devices:
        device = str(device)
        cmd = ['cio_ignore', '-r', device]
        out, error, rc = run_command(session, cmd)
        if rc:
            session.logging.info('failed to remove device "%s" from ignore list.'
                                 ' Error: %s' % (device, error))
            failed_devices.append(device)
    if failed_devices:
        raise Exception("Failed to remove devices '%s' from ignore list."
                        % remove_devices)
    session.logging.info('<--utils.remove_from_ignore_list()')


def run_command(session, command):
    session.logging.info('-->utils.run_command(): command :%s' % command)
    cmd_out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = cmd_out.communicate()
    returncode = cmd_out.returncode
    session.logging.info('<--utils.run_command()')
    return out, error, returncode


def configure_nwdevice(session, device_triplet):
    session.logging.info('-->utils.configure_nwdevice(): device:%s' % device_triplet)
    if not device_triplet or device_triplet.isspace():
        return
    device = device_triplet.split(',')[0]
    cmd = ['znetconf', '-a', device]
    session.logging.info('Configure network device "%s" using command "%s"'
                         % (device, cmd))
    out, err, rc = run_command(session, cmd)
    if rc:
        session.logging.info('Failed to configure network device "%s". Error: "%s"'
                         % (device, err))
        return 1
    cfg_file = ifcfg_path.replace('<deviceid>', device)
    cfg_content = ifcfg_content.replace(
                '<deviceid>', device).replace('<subchannels>', device_triplet)
    try:
        session.logging.info('create cfg file "%s" and write cfg params '
                             '"%s" for network device "%s"'
                             % (cfg_file, cfg_content, device))
        with open(cfg_file, 'w') as cfg_file:
            cfg_file.write(cfg_content)
    except Exception, err:
        session.logging.error(
            'Failed write ifcfg params %s in file %s. Error: %s' %
            (cfg_content, cfg_file, err))
        session.logging.info('<--utils.configure_nwdevice()')
        return 1
    session.logging.info('<--utils.configure_nwdevice()')
    return 0


def unconfigure_nwdevice(session, device_triplet):
    session.logging.info('-->utils.unconfigure_nwdevice(): device:%s' % device_triplet)
    if not device_triplet or device_triplet.isspace():
        return
    device = device_triplet.split(',')[0]
    cmd = ['znetconf', '-r', device, '-n']
    session.logging.info('checking if the network device %s is configured' % device)
    online_file_path = '/sys/bus/ccwgroup/devices/' + device + '/online'
    if not os.path.exists(online_file_path):
        # network device is not configured
        session.logging.info('network device "%s" is not configured' % device)
        return 0
    session.logging.info('un-configure network device "%s" using command "%s"'
                         %(device, cmd))
    out, err, rc = run_command(session, cmd)
    if rc:
        session.logging.info('Failed to un-configure network device "%s". '
                             'Error: "%s"' % (device, err))
        return 1
    cfg_file = ifcfg_path.replace('<deviceid>', device)
    if os.path.exists(cfg_file):
        try:
            session.logging.error(
                'Remove ifcfg file %s to un-persist network device %s.'
                %(cfg_file, device))
            os.remove(cfg_file)
        except Exception, err:
            session.logging.error(
                'Failed to remove ifcfg file %s. Error: %s' %(cfg_file, err))
            return 1
    session.logging.info('<--utils.unconfigure_nwdevice()')
    return 0


def bring_eckd_online(session, device):
    session.logging.info('-->utils.bring_eckd_online(): device:%s' % device)
    if not device or device.isspace():
        return
    command_bring_online = ['chccwdev', '-e', device]
    command_persist_dasdeckd = 'flock -w 1 %s -c \"echo %s >> %s\"' \
                               % (DASD_CONF, device, DASD_CONF)
    out, err, rc = run_command(session, command_bring_online)
    session.logging.info('bring eckd "%s" online using command "%s"'
                         % (device, command_bring_online))
    if rc:
        session.logging.info('Failed to bring eckd "%s" online. Error: %s'
                         % (device, err))
        return 1
    session.logging.info('persist eckd "%s" in "%s" with command "%s"' %
                     (device, DASD_CONF, command_persist_dasdeckd))
    if os.system(command_persist_dasdeckd):
        # persist dasd eckd in dasd.conf
        # return 1 if command fails
        session.logging.error('failed to persist zfcp "%s" in "%s" with '
                          'command "%s"' %
                          (device, DASD_CONF, command_persist_dasdeckd))
        return 1
    session.logging.info('<--utils.bring_eckd_online()')
    return 0


def bring_eckd_offline(session, device):
    session.logging.info('-->utils.bring_eckd_offline(): device:%s' % device)
    if not device or device.isspace():
        return
    command_bring_offline = ['chccwdev', '-d', device]
    command_unpersist_dasdeckd = 'flock -w 1 %s -c \"sed -i \'/%s/Id\' %s\"'\
                                 % (DASD_CONF, device, DASD_CONF)
    session.logging.info('bring eckd "%s" offline using command "%s"' % (device, command_bring_offline))
    out, err, rc = run_command(session, command_bring_offline)
    if rc:
        session.logging.info('Failed to bring eckd "%s" offline. Error: %s' % (device, err))
        return 1
    session.logging.info('un-persist eckd "%s" in "%s" with command "%s"' %
                         (device, DASD_CONF, command_unpersist_dasdeckd))
    if os.system(command_unpersist_dasdeckd):
        # unpersist dasd eckd from dasd.conf
        # return 1 if command fails
        session.logging.error('failed to un-persist eckd "%s" in "%s" with '
                              'command "%s"' %
                              (device, DASD_CONF, command_unpersist_dasdeckd))
        return 1
    session.logging.info('<--utils.bring_eckd_offline()')
    return 0


def bring_zfcp_online(session, device):
    session.logging.info('-->utils.bring_zfcp_online(): device:%s' % device)
    if not device or device.isspace():
        return
    command_bring_online = ['chccwdev', '-e', device]
    dummy_lun_info = '0x0000000000000000 0x0000000000000000'
    persist_data = device + ' ' + dummy_lun_info
    command_persist_zfcp = 'flock -w 1 %s -c \"echo %s >> %s\"' \
                           % (ZFCP_CONF, persist_data, ZFCP_CONF)
    session.logging.info('bring zfcp "%s" online using command "%s"'
                         % (device, command_bring_online))
    out, err, rc = run_command(session, command_bring_online)
    if rc:
        session.logging.info('Failed to bring zfcp "%s" online. Error: %s'
                             % (device, err))
        return 1
    session.logging.info('persist zfcp "%s" in "%s" with command "%s"' %
                         (device, ZFCP_CONF, command_persist_zfcp))
    if os.system(command_persist_zfcp):
        # persist zfcp device in zfcp.conf
        # return False if command fails
        session.logging.error('failed to persist zfcp "%s" in "%s" with '
                              'command "%s"' %
                              (device, ZFCP_CONF, command_persist_zfcp))
        return 1
    session.logging.info('<--utils.bring_zfcp_online()')
    return 0


def bring_zfcp_offline(session, device):
    """
    method to bring zfcp device online and persist in /etc/zfcp.conf
    Returns: 0 if success and 1 if failed

    """
    session.logging.info('-->utils.bring_zfcp_offline(): device:%s' % device)
    if not device or device.isspace():
        return
    command_bring_offline = ['chccwdev', '-d', device]
    command_unpersist_zfcp = 'flock -w 1 %s -c \"sed -i \'/%s/Id\' %s\"'\
                             % (ZFCP_CONF, device, ZFCP_CONF)
    session.logging.info('bring zfcp "%s" offline using command "%s"' % (device, command_bring_offline))
    out, err, rc = run_command(session, command_bring_offline)
    if rc:
        session.logging.info('Failed to bring zfcp "%s" offline. Error: %s' % (device, err))
        return 1
    session.logging.info('un-persist zfcp "%s" in "%s" with command "%s"' %
                         (device, ZFCP_CONF, command_unpersist_zfcp))
    if os.system(command_unpersist_zfcp):
        # unpersist zfcp device from zfcp.conf
        # return 1 if command fails
        session.logging.error('failed to un-persist zfcp "%s" in "%s" with '
                              'command "%s"' %
                              (device, ZFCP_CONF, command_unpersist_zfcp))
        return 1
    session.logging.info('<--utils.bring_zfcp_offline()')
    return 0