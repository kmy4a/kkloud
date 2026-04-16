import ansible_runner


def ping_to_fabric():
    """Ping the fabric to check its status using Ansible.

    Raises:
        RuntimeError: If the Ansible playbook execution fails.
    """
    r = ansible_runner.run(
        private_data_dir="../../ansible/",
        playbook="playbooks/ping.yml",
        quiet=True,
    )

    if r.rc != 0:
        raise RuntimeError("Failed to get fabric status")
