import ansible_runner


def ping_to_fabric():
    r = ansible_runner.run(
        private_data_dir='../../ansible/',
        playbook='playbooks/ping.yml',
        extravars={},
        quiet=True
    )

    if r.rc != 0:
        raise RuntimeError("Failed to get fabric status")
