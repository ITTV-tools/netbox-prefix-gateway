from netbox.plugins import PluginConfig

__version__ = "0.1.0"


class PrefixGatewayConfig(PluginConfig):
    name = "netbox_prefix_gateway"
    verbose_name = "Prefix Gateway"
    description = "Adds an optional Gateway field to prefixes"
    version = __version__
    author = "ITTV-tools"
    base_url = "prefix-gateway"
    min_version = "4.5.0"

    def ready(self):
        super().ready()
        from . import signals  # noqa: F401  (registers validation)
        from .ui import install_gateway_row

        install_gateway_row()


config = PrefixGatewayConfig
