import yaml
from ..model.subnet_models import Subnet


class SubnetLoader:
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
            yaml.dump(
                {"subnets": [subnet.model_dump() for subnet in self.subnets]}, file
            )

    def add(self, subnet: Subnet) -> None:
        """Add a new Subnet to the list and save it to the YAML file."""
        self.subnets.append(subnet)
        self._save()

    def delete(self, subnet_id: str) -> None:
        """Delete a Subnet by its ID and save the updated list to the YAML file."""
        self.subnets = [subnet for subnet in self.subnets if subnet.id != subnet_id]
        self._save()

    def update(self, subnet: Subnet) -> None:
        """Update an existing Subnet and save the updated list to the YAML file."""
        self.subnets = [s if s.id != subnet.id else subnet for s in self.subnets]
        self._save()


subnet_loader = SubnetLoader()
