terraform {
  required_providers {
    hcloud = {
      source                = "hetznercloud/hcloud"
      configuration_aliases = [hcloud]
    }
  }
}

resource "hcloud_firewall" "server_firewall" {
  name = var.name

  dynamic "rule" {
    for_each = var.rules
    content {
      direction  = rule.value.direction
      protocol   = rule.value.protocol
      port       = rule.value.port
      source_ips = rule.value.source_ips
    }
  }
}

resource "hcloud_firewall_attachment" "server_firewall_attachement" {
  firewall_id     = hcloud_firewall.server_firewall.id
  label_selectors = ["firewall-attachment=${var.firewall_attachment_label}"]
  depends_on      = [hcloud_firewall.server_firewall]
}
