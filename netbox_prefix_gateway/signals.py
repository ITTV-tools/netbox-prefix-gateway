from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.utils.translation import gettext as _

from ipam.models import IPAddress, Prefix
from netbox.signals import post_clean

from .constants import GATEWAY_FIELD


@receiver(post_clean, sender=Prefix)
def validate_gateway(sender, instance, **kwargs):
    """Make sure the gateway lies inside the prefix and its VRF."""
    gateway_id = (instance.custom_field_data or {}).get(GATEWAY_FIELD)
    if not gateway_id or not instance.prefix:
        return

    field = f"cf_{GATEWAY_FIELD}"
    gateway = IPAddress.objects.filter(pk=gateway_id).first()
    if gateway is None:
        raise ValidationError({field: _("The selected IP address does not exist.")})

    ip = gateway.address.ip
    net = instance.prefix
    if ip.version != net.version or ip not in net:
        raise ValidationError({field: _("Gateway {ip} is not inside prefix {prefix}.").format(ip=ip, prefix=net)})

    if gateway.vrf_id != instance.vrf_id:
        raise ValidationError({field: _("Gateway must be in the same VRF as the prefix.")})

    # Network and broadcast addresses can't be gateways (except /31, /32 and IPv6)
    if net.version == 4 and net.prefixlen < 31 and ip in (net.network, net.broadcast):
        raise ValidationError({field: _("Gateway can't be the network or broadcast address.")})
