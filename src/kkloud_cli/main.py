import requests
import sys


URL = "http://localhost:8000"

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: kkloud [vpcs|subnets] [options]")
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
    if args[0] == "list":
        list_vpcs()
    elif args[0] == "add":
        add_vpc(args[1], args[2])
    elif args[0] == "delete":
        delete_vpc(args[1])
    else:
        print(f"Usage: kkloud vpc list")
        print(f"Usage: kkloud vpc add <name> <cidr_block>")
        print(f"Usage: kkloud vpc delete <vpc_id>")


def subnet_controller(args: list[str]):
    if args[0] == "list":
        list_subnets(args[1])
    elif args[0] == "add":
        add_subnet(args[1], args[2], args[3])
    elif args[0] == "delete":
        delete_subnet(args[1], args[2])
    else:
        print(f"Usage: kkloud subnet list <vpc_id>")
        print(f"Usage: kkloud subnet get <vpc_id> <subnet_id>")
        print(f"Usage: kkloud subnet add <vpc_id> <name> <cidr_block>")
        print(f"Usage: kkloud subnet delete <vpc_id> <subnet_id>")


def list_vpcs():
    r = requests.get(f"{URL}/vpcs")
    print(r.json())


def add_vpc(name: str, cidr_block: str):
    r = requests.post(f"{URL}/vpcs", json={"name": name, "cidr_block": cidr_block})
    print(r.json())


def delete_vpc(vpc_id: str):
    r = requests.delete(f"{URL}/vpcs/{vpc_id}")
    print(r.json())


def list_subnets(vpc_id: str):
    r = requests.get(f"{URL}/vpcs/{vpc_id}/subnets")
    print(r.json())


def add_subnet(vpc_id: str, name: str, cidr_block: str):
    r = requests.post(f"{URL}/vpcs/{vpc_id}/subnets", json={"name": name, "cidr_block": cidr_block})
    print(r.json())


def delete_subnet(vpc_id: str, subnet_id: str):
    r = requests.delete(f"{URL}/vpcs/{vpc_id}/subnets/{subnet_id}")
    print(r.json())


def attach_igw(vpc_id: str):
    r = requests.post(f"{URL}/vpcs/{vpc_id}/igw")
    print(r.json())


def detach_igw(vpc_id: str):
    r = requests.delete(f"{URL}/vpcs/{vpc_id}/igw")
    print(r.json())


if __name__ == "__main__":
    main()