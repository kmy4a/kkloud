from ..model.vpc_models import VPC
import ansible_runner


async def create_vpc(vpc: VPC) -> None:
    """Create a VPC using Ansible playbook with the given VPC details.

    Raises:
        RuntimeError: If the Ansible playbook execution fails.
    """
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/create_vpc.yml",
        extravars={
            "vpc_name": vpc.name,
            "vpc_cidr_block": str(vpc.cidr_block),
            "vpc_vni": vpc.vni,
        },
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to create VPC: {vpc.id}")


async def delete_vpc(vpc: VPC) -> None:
    """Delete a VPC using Ansible playbook with the given VPC details.

    Raises:
        RuntimeError: If the Ansible playbook execution fails.
    """
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/delete_vpc.yml",
        extravars={
            "vpc_name": vpc.name,
            "vpc_cidr_block": str(vpc.cidr_block),
            "vpc_vni": vpc.vni,
        },
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to delete VPC: {vpc.id}")


async def attach_igw(vpc: VPC) -> None:
    """Attach an Internet Gateway (IGW) to a VPC using Ansible playbook with the given VPC details.

    Raises:
        RuntimeError: If the Ansible playbook execution fails.
    """
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/attach_igw.yml",
        extravars={
            "vpc_name": vpc.name,
            "vpc_cidr_block": str(vpc.cidr_block),
            "vpc_vni": vpc.vni,
        },
        quiet=True
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to attach IGW to VPC: {vpc.id}")


async def detach_igw(vpc: VPC) -> None:
    """Detach an Internet Gateway (IGW) from a VPC using Ansible playbook with the given VPC details.

    Raises:
        RuntimeError: If the Ansible playbook execution fails.
    """
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/detach_igw.yml",
        extravars={
            "vpc_name": vpc.name,
            "vpc_cidr_block": str(vpc.cidr_block),
            "vpc_vni": vpc.vni,
        },
        quiet=True
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to detach IGW from VPC: {vpc.id}")
