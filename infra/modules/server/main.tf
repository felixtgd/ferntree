terraform {
  required_providers {
    hcloud = {
      source                = "hetznercloud/hcloud"
      configuration_aliases = [hcloud]
    }
  }
}

resource "hcloud_primary_ip" "primary_ip" {
  name        = "${var.name}-primary-ip"
  location    = var.location
  type        = "ipv4"
  auto_delete = false
  labels      = var.labels
}

resource "hcloud_ssh_key" "ssh_key" {
  name       = "${var.name}-ssh-key"
  public_key = var.ssh_public_key
}

resource "hcloud_server" "server" {
  name        = "${var.project}-${var.name}"
  image       = var.image
  server_type = var.type
  location    = var.location
  labels      = var.labels
  ssh_keys    = [hcloud_ssh_key.ssh_key.id]
  user_data = templatefile("${path.module}/cloud-init.yaml", {
    ssh_public_key = var.ssh_public_key
    github_user    = var.github_user
    github_email   = var.github_email
  })
  public_net {
    ipv4_enabled = true
    ipv4         = hcloud_primary_ip.primary_ip.id
    ipv6_enabled = false
  }
  depends_on = [
    hcloud_primary_ip.primary_ip,
    hcloud_ssh_key.ssh_key
  ]
}
