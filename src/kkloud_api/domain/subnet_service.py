import yaml
import uuid
import ipaddress
from ..models.subnet_models import Subnet, RequestSubnet
from ..infrastructure import subnet_infrastructure as subnet_infra
from .vpc_service import vpcs


class Subnets:
    def __init__(self, data_file='data/subnet_repository.yml'):
        self.data_file = data_file
        self.subnets = self.load()

    def load(self) -> list[dict[str, str]]:
        with open(self.data_file, 'r') as file:
            data = yaml.safe_load(file)
            return data.get('subnets', [])

    def save(self) -> None:
        with open(self.data_file, 'w') as file:
            yaml.dump({'subnets': self.subnets}, file)

    def get_all(self, vpc_id: str) -> list[dict[str, str]]:
        return [subnet for subnet in self.subnets if subnet['vpc_id'] == vpc_id]

    def get(self, subnet_id: str) -> dict[str, str]:
        for subnet in self.subnets:
            if subnet['id'] == subnet_id:
                return subnet
        raise ValueError(f"Subnet with id {subnet_id} not found")

    def add(self, vpc_id: str, request_subnet: RequestSubnet) -> str:
        vpc: dict[str, str] = vpcs.get(vpc_id)
        vpc_subnet = vpc['cidr_block']
        if not ipaddress.IPv4Network(request_subnet.cidr_block).subnet_of(ipaddress.IPv4Network(vpc_subnet)):
            raise ValueError(f"Subnet CIDR block {request_subnet.cidr_block} is not within VPC CIDR block {vpc_subnet}")
        if any(ipaddress.IPv4Network(request_subnet.cidr_block).overlaps(ipaddress.IPv4Network(subnet['cidr_block'])) for subnet in self.get_all(vpc_id)):
            raise ValueError(f"Subnet CIDR block {request_subnet.cidr_block} overlaps with existing subnets in VPC {vpc_id}")

        subnet_obj = Subnet(
            id="subnet-"+str(uuid.uuid4()),
            vpc_id=vpc_id,
            name=str(request_subnet.name),
            cidr_block=str(request_subnet.cidr_block),
            vni=int(vpc['vni']) + len(self.get_all(vpc_id)) + 1
        )
        subnet_infra.create_subnet(subnet_obj, vpc)
        subnet_infra.enable_route_table(subnet_obj, self.get_all(vpc_id))
        self.subnets.append(subnet_obj.model_dump())
        self.save()
        return subnet_obj.id

    def delete(self, vpc_id: str, subnet_id: str) -> None:
        try:
            vpc: dict[str, str] = vpcs.get(vpc_id)
        except ValueError as e:
            raise RuntimeError(str(e))

        if not any(subnet['id'] == subnet_id and subnet['vpc_id'] == vpc_id for subnet in self.subnets):
            raise ValueError(f"Subnet with id {subnet_id} not found in VPC {vpc_id}")
        subnet = Subnet(
            id=subnet_id,
            vpc_id=vpc_id,
            name=next(subnet['name'] for subnet in self.subnets if subnet['id'] == subnet_id),
            cidr_block=next(subnet['cidr_block'] for subnet in self.subnets if subnet['id'] == subnet_id),
            vni=int(next(subnet['vni'] for subnet in self.subnets if subnet['id'] == subnet_id))
        )
        subnet_infra.delete_subnet(subnet, vpc)
        self.subnets = [subnet for subnet in self.subnets if subnet['id'] != subnet_id]
        self.save()


subnets = Subnets()
