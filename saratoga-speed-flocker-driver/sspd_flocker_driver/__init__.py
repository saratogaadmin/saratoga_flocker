from flocker.node import BackendDescription, DeployerType
from sspd_flocker_driver.sspd_blockdevice import sspd_flocker_api_setup


def api_factory(**kwargs):
    '''
        Current Assumptions:
           1. Node can't be configured with more then one LUN on Array.
           2. LUN's WWN needs to be provided with configuration of Flocker
           3. Create of Volume is validation of LD Exists on Array and then discover and login to iSCSI.
           4. Delete of Volume is validation of LD Exists and Disconnect iSCSI.
    '''
    return sspd_flocker_api_setup(sspdMgnHost=kwargs['sspdMgnHost'],
                                  sspdMgnUser=kwargs['sspdUser'],
                                  sspdMgnPassword=kwargs['sspdPassword'],
                                  sspdDataHost=kwargs['sspdDataHost'],
                                  sspdDeviceName=kwargs['sspdDeviceName'],
                                  ssdpDeviceWWN=kwargs['sspdDeviceWWN'])


FLOCKER_BACKEND = BackendDescription(
    name=u"saratoga_speed_flocker_plugin",
    needs_reactor=False, needs_cluster_id=False,
    api_factory=api_factory, deployer_type=DeployerType.block)
