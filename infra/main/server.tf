locals {
  dev_server_config = {
    image = "debian-12"
    type  = "cpx12"
    labels = {
      "project" : local.project,
      "datacenter" : local.datacenter,
      "firewall-attachment" : "dev-server"
    }
  }
  servers = {
    "dev-server-felix" = merge(
      local.dev_server_config,
      {
        ssh_public_key = file("~/.ssh/hetzner_key.pub")
        github_user    = "felixtgd"
        github_email   = "felix.tangerding@pm.me"
      }
    ),
  }
}

module "server" {
  source         = "../modules/server"
  for_each       = local.servers
  location       = local.datacenter
  project        = local.project
  name           = each.key
  labels         = each.value.labels
  image          = each.value.image
  type           = each.value.type
  ssh_public_key = each.value.ssh_public_key
  github_user    = each.value.github_user
  github_email   = each.value.github_email
  providers = {
    hcloud = hcloud
  }
}
