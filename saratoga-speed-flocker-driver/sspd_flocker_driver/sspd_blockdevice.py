import socket
import sys
import json
import urllib
import urllib2
import subprocess


from flocker.node.agents.blockdevice import (
    VolumeException, AlreadyAttachedVolume,
    UnknownVolume, UnattachedVolume,
    IBlockDeviceAPI, _blockdevicevolume_from_dataset_id,
    _blockdevicevolume_from_blockdevice_id
)


class SSpdConfiguration(object):
    def __init__(self, mgnHost, login, password, dataHost, deviceName, deviceWWN):
        self.loginUser = login
        self.loginPassword = password
        self.mgnHost = mgnHost
        self.loginHostURL = "http://" + mgnHost + "/sasp-app/sasp-app.py"
        self.dataHost = dataHost
        self.deviceName = deviceName
        self.deviceWWN = deviceWWN
        self.userSession = None
        
    def setUserSession(self, sessionId):
        self.userSession = sessionId
        

class SSpdMgmAPI(object):
    def __init__(self, configObj):
        self.spdConfig = configObj
        self.currentHost = None
        self.deviceId = None
        
        
    def _managementPort(self):
        return 80
        
        
    def _defaultMethodType(self):
        return "POST"
        
        
    def _setSCSIInitiatorId(self):
        self.deviceId = None
        # TODO:: Is is possible to have more then One interface..
        iscsin = os.popen('cat /etc/iscsi/initiatorname.iscsi').read()
        match = re.search('InitiatorName=.*', iscsin)
        if len(match.group(0)) > 13:
            self.deviceId = match.group(0)[14:]
        else:
            raise DeviceException(self.spdConfig)
            

    def setup(self):
        # Setup Headers
        self._setSCSIInitiatorId()
        # Login to Management
        self._login()
        
        
    def _setupRequestHeaders(self, request):
        request.add_header("Device-Id", self.deviceId)
        request.add_header("Remote-Address", self.currentHost)
        request.add_header("Content-Type", "application/json")

            
    def _login(self):
        args = {}
        attrList = {}
        args['opcode'] = 'webLogin'
        args['obj_type'] = 'session'
        attrList['username'] = self.spdConfig.loginUser
        attrList['password'] = self.spdConfig.loginPassword
        args['attr_list'] = attrList
        
        try:
            response = self.sendRequest(argsJson)
            if 'success' in response and response['success']:
                userSessionId = response['response']['session_id']
                self.spdConfig.setUserSession(userSessionId) 
            else:
                raise Exception("Response Unsuccessful")
        except Exception as e:
            raise DeviceException(self.spdConfig)
            
            
    def getLDWithName(self, logicalDriveName):
        args = {}
        attrList = {}
        args['session_id'] = self.sessionId #####
        args['opcode'] = 'getall'
        args['obj_type'] = 'logical_drive'
        args['attr_list'] = attrList
        try:
            response = self.sendRequest(argsJson)
            if 'success' in response and response['success'] and response['success'] == 1:
                ldResponse = response['response']
                for ldId, ldObj in ldResponse.items():
                    
            else:
                raise Exception("Response Unsuccessful")

        except Exception as e:
            raise DeviceException(self.spdConfig)

        
    def getAllTargets(self, matchDeviceId=False):
        args = {}
        attrList = {}
        args['session_id'] = self.sessionId #####
        args['opcode'] = 'getall'
        args['obj_type'] = 'target'
        args['attr_list'] = attrList
        
        try:
            response = self.sendRequest(argsJson)
            if 'success' in response and response['success'] and response['success'] == 1:
                targetResponse = response['response']
                #TODO: Currently Assumption is only one Storage is available per Flocker Client
                
                self._findDeviceLun(targetResponse) 
            else:
                raise Exception("Response Unsuccessful")

        except Exception as e:
            raise DeviceException(self.spdConfig)
            
            
    def sendRequest(self, requestJson):
        responseObj = {}
        try:
            argsJson = json.dumps(requestJson)
            request = urllib2.Request(self.loginHostURL, argsJson)
            request.get_method = lambda: self._defaultMethodType()
            self._setupRequestHeaders(request)
            
            returnObj = urllib2.urlopen(request)
            if (returnObj.status == 200):
                strResponse = response.read().decode('utr-8')
                responseObj = json.loads(strResponse, object_hook=byteify)
            else:
                raise Exception("Error in Response")
        except Exception as e:
            raise e
            
        return responseObj
        
        
    def _findDeviceLun(self, targetsDict):
        for trgId, trgObj in targetResponse.items():
            print "%s" %trgId
            if not trgObj['demo'] and trgObj['state'] == 'Active':
                acls = trgObj['target_acls']
                if len(acls) > 0:
                    for aclId, aclObj in acls.items():
                        if self.deviceId == aclId and aclObj['state'] == 'Active':
                            return trgId
        return None


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
        

        
'''
    Flocker setup method.. To get started with Saratoga Speed Array..
'''
def sspd_flocker_api_setup(sspdMgnHost, sspdMgnUser, sspdMgnPassword, ssdpDataHost, sspdDeviceName, ssdpDeviceWWN):

    return EMCXtremIOBlockDeviceAPI(
        configuration=SSpdConfiguration(sspdMgnHost, sspdMgnUser, sspdMgnPassword, ssdpMgnDataHost, sspdDeviceName, ssdpDeviceWWN),
        compute_instance_id=unicode(socket.gethostname()),
        allocation_unit=1
    )
    


@implementer(IBlockDeviceAPI)
class SSpdFlockerBlockDeviceAPI(object):
    def __init__(self, configuration, compute_instance_id=unicode(socket.gethostname()), allocation_unit = 1):
        self.config = configuration
        self.instanceId = compute_instance_id
        self.allocationUnit = allocation_unit
        
        
    def allocation_unit():
        return self.allocationUnit

    def compute_instance_id():
        return instanceId

    def create_volume(dataset_id, size):
        # Validat if LD name provided in configuration exist and is attached to proper Target

    def destroy_volume(blockdevice_id):
        # Again just to validation similar to in Create and return success nothing to do here..

    def attach_volume(blockdevice_id, attach_to):
        # Login iSCSI (iscsiadm)

    def detach_volume(blockdevice_id):
        # Logout iSCSI (iscsiadm -u)

    def list_volumes():
        '''
            Currently list_volumes has a bug where it does not have a state 
            where we can return if volume is attached to any client.
        '''
        

    def get_device_path(blockdevice_id):
    
        
        
    def _scsiDeviceExists(self, scsiTargetId, interfaceHost):
        cmdArray = ["iscsiadm", "-m", "discovery", "-t", "st", "-p", interfaceHost]
        cmdOut = subprocess.check_output(cmdArray)
        for rLine in cmdOut.split('\n'):
            if re.search(scsiTargetId, rLine, re.I):
                return True
        return False
        
    def _scsiDeviceLogin(self, scsiTargetId, interfaceHost):
        cmdArray = ["iscsiadm", "-m", "node", "-T", scsiTargetId, "-p", interfaceHost, "-l"]
        cmdOut = subprocess.check_output(cmdArray)
        
    def _scsiDevice(self, scsiTargetId):
        cmdArray = ["ls", "-al", "/dev/disk/by-path/"]
        cmdOut = subprocess.check_output(cmdArray)
        for rLine in cmdOut.split('\n'):
            if re.search(scsiTargetId, rLine, re.I):
                outSplitArray = rLine.split(" -> ")
                if len(outSplitArray) > 1:
                    deviceId = outSplitArray[len(outSplitArray) - 1]
                    deviceIdArray = deviceId.split("../../")
                    devName = deviceIdArray[len(deviceIdArray) - 1]
                    deviceWithPath = "/dev/%s" %devName
                    return deviceWithPath
        return None
        
    
    
class VolumeExists(VolumeException):
    """
    Request for creation of an existing volume
    """


class VolumeAttached(VolumeException):
    """
    Attempting to destroy an attached volume
    """


class InvalidVolumeMetadata(VolumeException):
    """
    Volume queried or supplied has invalid data
    """


class VolumeBackendAPIException(Exception):
    """
    Exception from backed mgmt server
    """


class DeviceException(Exception):
    """
    A base class for exceptions raised by  ``IBlockDeviceAPI`` operations.
    Due to backend device configuration

    :param ArrayConfiguration configuration: The configuration related to backend device.
    """

    def __init__(self, configuration):
        if not isinstance(configuration, SSpdConfiguration):
            raise TypeError(
                'Unexpected configuration type. '
                'Expected ArrayConfiguration. '
                'Got {!r}.'.format(AttributeError)
            )
        Exception.__init__(self, configuration)


class DeviceVersionMismatch(DeviceException):
    """
    The version of device not supported.
    """


class DeviceExceptionObjNotFound(Exception):
    """
    The Object not found on device
    """

