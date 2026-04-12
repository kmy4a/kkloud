from ..models.vpc_models import VPC
import ansible_runner


def create_vpc(vpc: VPC) -> None:
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/create_vpc.yml",
        extravars={
            "vpc_name": vpc.name,
            "vpc_cidr_block": vpc.cidr_block,
            "vpc_vni": vpc.vni,
        },
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to create VPC: {vpc.id}")


def delete_vpc(vpc: VPC) -> None:
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/delete_vpc.yml",
        extravars={
            "vpc_name": vpc.name,
            "vpc_cidr_block": vpc.cidr_block,
            "vpc_vni": vpc.vni,
        },
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to delete VPC: {vpc.id}")


def attach_igw(vpc: VPC) -> None:
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/attach_igw.yml",
        extravars={
            "vpc_name": vpc.name,
            "vpc_cidr_block": vpc.cidr_block,
            "vpc_vni": vpc.vni,
        },
        # quiet=True
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to attach IGW to VPC: {vpc.id}")


def detach_igw(vpc: VPC) -> None:
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/detach_igw.yml",
        extravars={
            "vpc_name": vpc.name,
            "vpc_cidr_block": vpc.cidr_block,
            "vpc_vni": vpc.vni,
        },
        # quiet=True
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to detach IGW from VPC: {vpc.id}")
