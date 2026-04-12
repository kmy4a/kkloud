from ..models.subnet_models import Subnet
import ansible_runner


def create_subnet(subnet: Subnet, vpc: dict[str, str]):
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/create_subnet.yml",
        extravars={
            "vpc_name": vpc["name"],
            "subnet_name": subnet.name,
            "subnet_cidr_block": subnet.cidr_block,
            "subnet_vni": subnet.vni,
        },
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to create Subnet: {subnet.id}")


def enable_route_table(subnet: Subnet, routes: list[dict[str, str]]):
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/enable_route_table.yml",
        extravars={
            "subnet_name": subnet.name,
            "subnet_cidr_block": subnet.cidr_block,
            "subnet_vni": subnet.vni,
            "routes": routes,
        },
        # quiet=True
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to enable route table for Subnet: {subnet.id}")


def delete_subnet(subnet: Subnet, vpc: dict[str, str]):
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/delete_subnet.yml",
        extravars={
            "vpc_name": vpc["name"],
            "subnet_name": subnet.name,
            "subnet_cidr_block": subnet.cidr_block,
            "subnet_vni": subnet.vni,
        },
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError(f"Failed to delete Subnet: {subnet.id}")
