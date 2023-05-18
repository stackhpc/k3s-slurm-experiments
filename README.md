# k3s-cluster-experiments

Demo of creating a k3s cluster.

- Terraform is used to create 3x nodes.
- Ansible builds an in-memory inventory from terraform output.
- The k3s role is split into an "install" stage which could be run during image build and a "configure" stage which
  would ideally be run during boot.
- Currently this templates out the k3s service file during the "configure" stage, as the inventory-defined token cannot be assumed to be known at "install" time. It'd be nice to pass that dynamically somehow.

## Install

    python3.9 -m venv venv
    . venv/bin/activate
    pip install -U pip
    pip install ansible
    terraform init

## Run

    terraform apply
    ansible-playbook site.yml

## Usage

    terraform output
    ssh rocky@<k3s-control IP>
    export KUBECONFIG=~/.kube/config
    kubectl ...
