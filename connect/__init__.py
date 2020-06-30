from .connect import DKConnect, DKConnectError, DKConnectResponseTimoutError, DKConnectCommandsMismatch, DKConnectGotErrorCode
from .tank import DKTankCommands
from .bootloader import DKBootloaderCommands


DEVICE_BOOTLOADER = DKBootloaderCommands.DEVICE_NAME
DEVICE_TANK = DKTankCommands.DEVICE_NAME
DEVICE_UNIT = 'DK Unit'


DEVICES_ESSENTIAL_LIST = [DEVICE_TANK, DEVICE_UNIT]


COMMANDS_MAP = {
    DEVICE_BOOTLOADER: DKBootloaderCommands,
    DEVICE_TANK: DKTankCommands,
    DEVICE_UNIT: DKTankCommands,
}


def build_commands(con: DKConnect):
    return COMMANDS_MAP[con.device_name()](con)


def make_commands():
    con = DKConnect()
    if con.find_and_connect():
        return build_commands(con)

    return
