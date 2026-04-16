from ..infrastructure.vpc_loader import vpc_loader
from ..infrastructure.subnet_loader import subnet_loader
from ..infrastructure.fabric_runner import fabric_devices, ping_to_fabric


class Fabrics:
    def __init__(self):
        self.subnet = subnet_loader
        self.vpc = vpc_loader
        self.fabric_devices = fabric_devices
        self.fabric_devices.open()

    def health_check(self):
        """Check the health of the fabric."""
        self._check_configurations()
        if not all([self._ping_to_fabric()]):
            raise RuntimeError("Fabric health check failed")

    def _check_configurations(self):
        """Check the configurations of the fabric.

        Raises:
            RuntimeError: If the configurations of the fabric are not correct.
        """
        configs = self.fabric_devices.get_running_config()
        for config in configs:
            config_lines: list[str] = [line.strip() for line in config.splitlines()]
            if not self._check_vpcs(config_lines):
                raise RuntimeError("VPC check failed")
            if not self._check_subnets(config_lines):
                raise RuntimeError("VLAN check failed")
            if not self._check_igw(config_lines):
                raise RuntimeError("IGW check failed")

    def _check_vpcs(self, config_lines: list[str]) -> bool:
        """Check the VPCs of the fabric."""
        for vpc in self.vpc.vpcs:
            if f"vrf instance {vpc.name}" not in config_lines:
                return False
            if f"ip routing vrf {vpc.name}" not in config_lines:
                return False
            if f"vxlan vrf {vpc.name} vni {vpc.vni}" not in config_lines:
                return False
            if f"route-target import evpn {vpc.vni}:{vpc.vni}" not in config_lines:
                return False
            if f"route-target export evpn {vpc.vni}:{vpc.vni}" not in config_lines:
                return False
            if f"route-target both {vpc.vni + 1}:{vpc.vni + 1}" not in config_lines:
                return False
        return True

    def _check_subnets(self, config_lines: list[str]) -> bool:
        """Check the VLANs of the fabric."""
        for subnet in self.subnet.subnets:
            if f"vlan {subnet.vni}" not in config_lines:
                return False
            if f"interface Vlan{subnet.vni}" not in config_lines:
                return False
            if f"vxlan vlan {subnet.vni} vni {subnet.vni}" not in config_lines:
                return False
        return True

    def _check_igw(self, config_lines: list[str]) -> bool:
        """Check the IGW of the fabric."""
        for vpc in self.vpc.vpcs:
            if vpc.is_attached_to_igw:
                if f"route-target import evpn 65535:{vpc.vni}" not in config_lines:
                    return False
            else:
                if f"route-target import evpn 65535:{vpc.vni}" in config_lines:
                    return False
        return True

    def _ping_to_fabric(self) -> bool:
        """Ping the fabric to check its status."""
        try:
            ping_to_fabric()
            return True
        except RuntimeError:
            return False


fabrics = Fabrics()
