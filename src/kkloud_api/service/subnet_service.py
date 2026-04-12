import yaml
import uuid
import ipaddress
from ..model.subnet_models import Subnet, RequestSubnet
from ..model.vpc_models import VPC
from ..infrastructure import subnet_infrastructure as subnet_infra
from .vpc_service import vpcs


class Subnets:
    def __init__(self, data_file="data/subnet_repository.yml"):
        """Initialize the Subnets service with the specified data file."""
        self._data_file: str = data_file
        self.subnets: list[Subnet] = self._load()

    def _load(self) -> list[Subnet]:
        """Load Subnets from the YAML file."""
        with open(self._data_file, "r") as file:
            data = yaml.safe_load(file)
            return [Subnet(**subnet) for subnet in data.get("subnets", [])]

    def _save(self) -> None:
        """Save the current list of Subnets to the YAML file."""
        with open(self._data_file, "w") as file:
            yaml.dump({"subnets": [subnet.model_dump() for subnet in self.subnets]}, file)

    def get_all(self, vpc_id: str) -> list[Subnet]:
        """Return a list of all Subnets for a given VPC ID."""
        return [subnet for subnet in self.subnets if subnet.vpc_id == vpc_id]

    def get(self, subnet_id: str) -> Subnet:
        """Return a Subnet by its ID.

        Raises:
            ValueError: If the Subnet with the specified ID is not found.
        """
        for subnet in self.subnets:
            if subnet.id == subnet_id:
                return subnet
        raise ValueError(f"Subnet with id {subnet_id} not found")

    def add(self, vpc_id: str, request_subnet: RequestSubnet) -> str:
        """Add a new Subnet to a VPC based on the provided request data.

        Returns:
            subnet_id (str): The ID of the newly created Subnet.
        Raises:
            ValueError: If the VPC with the specified ID is not found, if the Subnet CIDR block is not within the VPC CIDR block, or if the Subnet CIDR block overlaps with existing Subnets in the VPC.
            RuntimeError: If the Subnet creation fails.
        """
        vpc: VPC = vpcs.get(vpc_id)
        vpc_subnet = vpc.cidr_block
        if not ipaddress.IPv4Network(request_subnet.cidr_block).subnet_of(
            ipaddress.IPv4Network(vpc_subnet)
        ):
            raise ValueError(
                f"Subnet CIDR block {request_subnet.cidr_block} is not within VPC CIDR block {vpc_subnet}"
            )
        if any(
            ipaddress.IPv4Network(request_subnet.cidr_block).overlaps(subnet.cidr_block)
            for subnet in self.get_all(vpc_id)
        ):
            raise ValueError(
                f"Subnet CIDR block {request_subnet.cidr_block} overlaps with existing subnets in VPC {vpc_id}"
            )

        subnet_obj = Subnet(
            id="subnet-" + str(uuid.uuid4()),
            vpc_id=vpc_id,
            name=request_subnet.name,
            cidr_block=request_subnet.cidr_block,
            vni=int(vpc.vni) + len(self.get_all(vpc_id)) + 1,
        )

        try:
            subnet_infra.create_subnet(subnet_obj, vpc)
            # subnet_infra.enable_route_table(subnet_obj, self.get_all(vpc_id))
        except RuntimeError:
            raise RuntimeError(f"Failed to create Subnet with id {subnet_obj.id} in VPC {vpc_id}")

        self.subnets.append(subnet_obj)
        self._save()
        return subnet_obj.id

    def delete(self, vpc_id: str, subnet_id: str) -> None:
        """Delete a Subnet from a VPC.

        Raises:
            ValueError: If the VPC with the specified ID is not found, or if the Subnet with the specified ID is not found in the VPC.
            RuntimeError: If the Subnet deletion fails.
        """
        try:
            vpc: VPC = vpcs.get(vpc_id)
        except ValueError as e:
            raise RuntimeError(str(e))

        if not any(
            subnet.id == subnet_id and subnet.vpc_id == vpc_id
            for subnet in self.subnets
        ):
            raise ValueError(f"Subnet with id {subnet_id} not found in VPC {vpc_id}")
        subnet = Subnet(
            id=subnet_id,
            vpc_id=vpc_id,
            name=next(
                subnet.name for subnet in self.subnets if subnet.id == subnet_id
            ),
            cidr_block=next(
                subnet.cidr_block
                for subnet in self.subnets
                if subnet.id == subnet_id
            ),
            vni=int(
                next(
                    subnet.vni
                    for subnet in self.subnets
                    if subnet.id == subnet_id
                )
            ),
        )

        try:
            subnet_infra.delete_subnet(subnet, vpc)
        except RuntimeError:
            raise RuntimeError(f"Failed to delete Subnet with id {subnet_id} in VPC {vpc_id}")

        self.subnets = [subnet for subnet in self.subnets if subnet.id != subnet_id]
        self._save()


subnets = Subnets()
