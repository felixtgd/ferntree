locals {
  allowed_ips = [
    "31.10.137.169", # Felix
  ]

  firewalls = {
    "dev-server-firewall" = {
      rules = [
        {
          direction  = "in"
          protocol   = "tcp"
          port       = "2222" # Custom SSH port
          source_ips = local.allowed_ips
        },
        {
          direction  = "in"
          protocol   = "tcp"
          port       = "80"          # HTTP
          source_ips = ["0.0.0.0/0"] # local.allowed_ips
        },
        {
          direction  = "in"
          protocol   = "tcp"
          port       = "443" # HTTPS
          source_ips = local.allowed_ips
        },
        {
          direction  = "in"
          protocol   = "icmp" # allow ICMP for ping (useful for debugging)
          port       = null
          source_ips = local.allowed_ips
        }
      ]
      firewall_attachment_label = "dev-server"
    }
  }
}

module "firewall" {
  source                    = "../modules/firewall"
  for_each                  = local.firewalls
  name                      = each.key
  rules                     = each.value.rules
  firewall_attachment_label = each.value.firewall_attachment_label
  depends_on                = [module.server]
  providers = {
    hcloud = hcloud
  }
}
