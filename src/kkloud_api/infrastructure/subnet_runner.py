from ..model.subnet_models import Subnet
from ..model.vpc_models import VPC
import ansible_runner


def create_subnet(subnet: Subnet, vpc: VPC) -> None:
    """Create a Subnet within a VPC using Ansible playbook with the given Subnet and VPC details.

    Raises:
        RuntimeError: If the Ansible playbook execution fails.
    """
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/create_subnet.yml",
        extravars={
            "vpc_name": vpc.name,
            "subnet_name": subnet.name,
            "subnet_cidr_block": str(subnet.cidr_block),
            "subnet_vni": subnet.vni,
        },
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to create Subnet: {subnet.id}")


def delete_subnet(subnet: Subnet, vpc: VPC) -> None:
    """Delete a Subnet from a VPC using Ansible playbook with the given Subnet and VPC details.

    Raises:
        RuntimeError: If the Ansible playbook execution fails.
    """
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/delete_subnet.yml",
        extravars={
            "vpc_name": vpc.name,
            "subnet_name": subnet.name,
            "subnet_cidr_block": str(subnet.cidr_block),
            "subnet_vni": subnet.vni,
        },
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to delete Subnet: {subnet.id}")
