class VPCNotFoundError(Exception):
    pass


class VPCDeletionError(Exception):
    pass


class SubnetNotFoundError(Exception):
    pass


class SubnetInvalidCIDRError(Exception):
    pass


class SubnetOverlapError(Exception):
    pass
