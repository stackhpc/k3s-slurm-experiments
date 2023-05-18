terraform {
  required_version = ">= 0.14"
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

resource "openstack_compute_instance_v2" "test" {

  for_each = toset(["control", "compute-0", "compute-1"])

  name = "k3s-${each.key}"
  image_name = "Rocky-8-GenericCloud-8.6.20220702.0.x86_64.qcow2"
  flavor_name = "vm.ska.cpu.general.small"
  key_pair = "slurm-app-ci"
  
  network {
    name = "portal-internal"
    access_network = true
  }

  user_data = <<-EOF
    #cloud-config
    user:
        homedir: /var/lib/cloud-user
  EOF

}

output "ips" {
    value = {for o in openstack_compute_instance_v2.test: o.name => o.network[0].fixed_ip_v4}
}
