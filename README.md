# k3s-cluster-experiments

Demo of creating a k3s cluster.

- Ansible runs Terraform is used to create 3x nodes.
- Ansible builds an in-memory inventory from Terraform output.
- The k3s role is split into an "install" stage which could be run during image build and a "configure" stage which
  would ideally be run during boot.
- The server token is passed using the `--token-file` flag in the service's `ExecStart`; therefore it is not visible from e.g. `systemctl show ...` or `ps`.
- Currently the (hardcoded!) server token file is created via Ansible; it'd be nice to pass this via e.g. cloud-init, but this does require templating the TF from ansible.
- The `--cluster-init` flag could be added to the FIRST server node to provide an HA cluster with embedded `etcd` (might cause potential timing issues). See [here](https://docs.k3s.io/datastore/ha-embedded).

Note the infrastructure is defined using ("all"-group) group-vars in `inventory/config.yml`. Simple continuous Slurm [node range expressions](https://slurm.schedmd.com/scontrol.html#OPT_hostlist) such as `compute-[0-1]` may be used to define multiple nodes at once. The `cluster_node_defaults` variable provides any variables undefined for a particular node.

## Install

    python3.9 -m venv venv
    . venv/bin/activate
    pip install -U pip
    pip install -r requirements.txt

Ensure a `clouds.yaml` file is available.

## Run
    
    export OS_CLOUD=openstack
    ansible-playbook infra.yml  # creates infrastructure
    ansible-playbook site.yml   # configures k3s etc

Note `infra.yml` is broken out as a separate playbook to make `site.yml` faster.

## Optional plays

Rebuild all instances with their current image (i.e., undo `site.yml`):

    ansible-playbook rebuild.yml

Destroy infrastructure:

    ansible-playbook infra.yml -e terraform_state=absent

## Usage

    terraform output
    ssh cloud-user@<k3s-control IP>
    export KUBECONFIG=~/.kube/config
    kubectl ...

### Some thoughts on passing secrets in metadata
Potentially:
- Set the token in metadata (which means driving ansible from TF)
- Use `disable_ec2_metadata`, and check whether the instance can still retrieve it (either as root, or from disk)
- Write a bootscript which runs `echo $token_from_metadata > systemd-creds encrypt - somepath/mycred`
- Use the following in the unit file:
        LoadCredentialEncrypted=path
        ExecStart= ... ${CREDENTIALS_DIRECTORY}/mycred
- Instructions: https://smallstep.com/blog/systemd-creds-hardware-protected-secrets/

However this looks problematic:

    # don't have TPM - looks like this needs Victoria or later on OpenStack + configuration:
    [rocky@k3s-control ~]$ sudo dmesg | grep TPM
    [    1.019778] ima: No TPM chip found, activating TPM-bypass!

    # need systemd 250+:
    [rocky@k3s-control ~]$ systemctl --version
    systemd 239 (239-58.el8)
