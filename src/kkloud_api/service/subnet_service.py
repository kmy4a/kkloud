import uuid
from ipaddress import IPv4Network
from ..model.subnet_models import Subnet, RequestSubnet
from ..model.vpc_models import VPC
from ..infrastructure import subnet_runner as subnet_infra
from ..infrastructure.subnet_loader import subnet_loader
from ..infrastructure.vpc_loader import vpc_loader
from ..infrastructure.logger import logger
from ..exceptions import (
    VPCNotFoundError,
    SubnetInvalidCIDRError,
    SubnetOverlapError,
    SubnetNotFoundError,
)


class Subnets:
    def __init__(self):
        """Initialize the Subnets service with the specified data file."""
        self.vpc_loader = vpc_loader
        self.subnet_loader = subnet_loader
        self.logger = logger

    def get_all(self, vpc_id: str) -> list[Subnet]:
        """Return a list of all Subnets for a given VPC ID."""
        return [
            subnet for subnet in self.subnet_loader.subnets if subnet.vpc_id == vpc_id
        ]

    def get(self, subnet_id: str) -> Subnet:
        """Return a Subnet by its ID.

        Raises:
            ValueError: If the Subnet with the specified ID is not found.
        """
        for subnet in self.subnet_loader.subnets:
            if subnet.id == subnet_id:
                return subnet
        raise SubnetNotFoundError(f"Subnet with id {subnet_id} not found")

    def add(self, vpc_id: str, request_subnet: RequestSubnet) -> str:
        """Add a new Subnet to a VPC based on the provided request data.

        Returns:
            subnet_id (str): The ID of the newly created Subnet.
        Raises:
            VPCNotFoundError: If the VPC with the specified ID is not found.
            SubnetInvalidCIDRError: If the Subnet CIDR block is not within the VPC CIDR block.
            SubnetOverlapError: If the Subnet CIDR block overlaps with existing Subnets in the VPC.
            RuntimeError: If the Subnet creation fails.
        """
        # Validate VPC existence
        for v in self.vpc_loader.vpcs:
            if v.id == vpc_id:
                vpc: VPC = v
                break
        else:
            raise VPCNotFoundError(f"VPC with id {vpc_id} not found")

        # Validate Subnet CIDR block is within VPC CIDR block
        vpc_subnet = vpc.cidr_block
        if not IPv4Network(request_subnet.cidr_block).subnet_of(
            IPv4Network(vpc_subnet)
        ):
            raise SubnetInvalidCIDRError(
                f"Subnet CIDR block {request_subnet.cidr_block} is not within VPC CIDR block {vpc_subnet}"
            )

        # Validate Subnet CIDR block does not overlap with existing Subnets in the VPC
        if any(
            IPv4Network(request_subnet.cidr_block).overlaps(subnet.cidr_block)
            for subnet in self.get_all(vpc_id)
        ):
            raise SubnetOverlapError(
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
        except RuntimeError:
            raise RuntimeError(
                f"Failed to create Subnet with id {subnet_obj.id} in VPC {vpc_id}"
            )

        self.subnet_loader.add(subnet_obj)
        self.logger.info(f"Created Subnet with id {subnet_obj.id} in VPC {vpc_id}")
        return subnet_obj.id

    def delete(self, vpc_id: str, subnet_id: str) -> None:
        """Delete a Subnet from a VPC.

        Raises:
            VPCNotFoundError: If the VPC is not found.
            SubnetNotFoundError: If the Subnet is not found.
            RuntimeError: If the Subnet deletion fails.
        """
        # Validate VPC existence
        for v in self.vpc_loader.vpcs:
            if v.id == vpc_id:
                vpc: VPC = v
                break
        else:
            raise VPCNotFoundError(f"VPC with id {vpc_id} not found")

        # Validate Subnet existence within the VPC
        for subnet in self.subnet_loader.subnets:
            if subnet.id == subnet_id and subnet.vpc_id == vpc_id:
                subnet: Subnet = subnet
                break
        else:
            raise SubnetNotFoundError(
                f"Subnet with id {subnet_id} not found in VPC {vpc_id}"
            )

        try:
            subnet_infra.delete_subnet(subnet, vpc)
        except RuntimeError:
            raise RuntimeError(
                f"Failed to delete Subnet with id {subnet_id} in VPC {vpc_id}"
            )

        self.subnet_loader.delete(subnet_id)
        self.logger.info(f"Deleted Subnet with id {subnet_id} in VPC {vpc_id}")


subnets = Subnets()
