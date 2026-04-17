import requests
import sys
import json


URL = "http://localhost:8000/api/v1"

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: kkloud [vpc|subnet] [options]")
        return

    command = args[0]
    if command == "vpc":
        vpc_controller(args[1:])
    elif command == "subnet":
        subnet_controller(args[1:])
    else:
        print(f"Unknown command: {command}")
        return


def vpc_controller(args: list[str]):
    if not args:
        print(f"Usage: kkloud vpc [list|add|delete|attach-igw|detach-igw] [options]")
        return

    if args[0] == "list":
        list_vpcs()
    elif args[0] == "add":
        if len(args) < 3:
            print(f"Usage: kkloud vpc add <name> <cidr_block>")
            return
        add_vpc(args[1], args[2])
    elif args[0] == "delete":
        if len(args) < 2:
            print(f"Usage: kkloud vpc delete <vpc_id>")
            return
        delete_vpc(args[1])
    elif args[0] == "attach-igw":
        if len(args) < 2:
            print(f"Usage: kkloud vpc attach-igw <vpc_id>")
            return
        attach_igw(args[1])
    elif args[0] == "detach-igw":
        if len(args) < 2:
            print(f"Usage: kkloud vpc detach-igw <vpc_id>")
            return
        detach_igw(args[1])
    else:
        print(f"Usage: kkloud vpc list")
        print(f"Usage: kkloud vpc add <name> <cidr_block>")
        print(f"Usage: kkloud vpc delete <vpc_id>")


def subnet_controller(args: list[str]):
    if not args:
        print(f"Usage: kkloud subnet [list|add|delete] [options]")
        return

    if args[0] == "list":
        if len(args) < 2:
            print(f"Usage: kkloud subnet list <vpc_id>")
            return
        list_subnets(args[1])
    elif args[0] == "add":
        if len(args) < 4:
            print(f"Usage: kkloud subnet add <vpc_id> <name> <cidr_block>")
            return
        add_subnet(args[1], args[2], args[3])
    elif args[0] == "delete":
        if len(args) < 3:
            print(f"Usage: kkloud subnet delete <vpc_id> <subnet_id>")
            return
        delete_subnet(args[1], args[2])
    else:
        print(f"Usage: kkloud subnet list <vpc_id>")
        print(f"Usage: kkloud subnet add <vpc_id> <name> <cidr_block>")
        print(f"Usage: kkloud subnet delete <vpc_id> <subnet_id>")


def list_vpcs():
    r = requests.get(f"{URL}/vpcs")
    print(json.dumps(r.json(), indent=2))


def add_vpc(name: str, cidr_block: str):
    r = requests.post(f"{URL}/vpcs", json={"name": name, "cidr_block": cidr_block})
    print(json.dumps(r.json(), indent=2))


def delete_vpc(vpc_id: str):
    r = requests.delete(f"{URL}/vpcs/{vpc_id}")
    print("VPC deleted successfully" if r.status_code == 204 else json.dumps(r.json(), indent=2))


def list_subnets(vpc_id: str):
    r = requests.get(f"{URL}/vpcs/{vpc_id}/subnets")
    print(json.dumps(r.json(), indent=2))


def add_subnet(vpc_id: str, name: str, cidr_block: str):
    r = requests.post(f"{URL}/vpcs/{vpc_id}/subnets", json={"name": name, "cidr_block": cidr_block})
    print(json.dumps(r.json(), indent=2))


def delete_subnet(vpc_id: str, subnet_id: str):
    r = requests.delete(f"{URL}/vpcs/{vpc_id}/subnets/{subnet_id}")
    print("VPC deleted successfully" if r.status_code == 204 else json.dumps(r.json(), indent=2))


def attach_igw(vpc_id: str):
    r = requests.post(f"{URL}/vpcs/{vpc_id}/igw")
    print(json.dumps(r.json(), indent=2))


def detach_igw(vpc_id: str):
    r = requests.delete(f"{URL}/vpcs/{vpc_id}/igw")
    print("IGW detached successfully" if r.status_code == 204 else json.dumps(r.json(), indent=2))


if __name__ == "__main__":
    main()
