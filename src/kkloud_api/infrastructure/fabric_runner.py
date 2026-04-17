import yaml
from ipaddress import IPv4Address
from napalm import get_network_driver
import ansible_runner


class FabricDevices:
    def __init__(self):
        self._instances = []
        for addr in self._get_ansible_hosts().values():
            eos_driver = get_network_driver("eos")
            device = eos_driver(
                hostname=str(addr),
                username="admin",
                password="admin",
            )
            self._instances.append(device)

    def open(self):
        """Open connections to all fabric devices."""
        for instance in self._instances:
            instance.open()

    def close(self):
        """Close connections to all fabric devices."""
        for instance in self._instances:
            instance.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, _, __, ___):
        self.close()

    def _get_ansible_hosts(self) -> dict[str, IPv4Address]:
        """Parse the Ansible inventory file to get the hosts in the fabric."""
        with open("../../ansible/inventory.yml", "r") as f:
            inventory = yaml.safe_load(f)
        hosts = {}
        for host, host_vars in inventory["all"]["children"]["fabric"]["children"][
            "leaf"
        ]["hosts"].items():
            hosts[host] = IPv4Address(host_vars["ansible_host"])
        return hosts

    def get_running_config(self):
        """Get the running configuration of the fabric."""
        return [instance.get_config()["running"] for instance in self._instances]


fabric_devices = FabricDevices()


def ping_to_fabric():
    """Ping the fabric to check its status using Ansible.

    Raises:
        RuntimeError: If the Ansible playbook execution fails.
    """
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/ping.yml",
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError("Failed to get fabric status")
