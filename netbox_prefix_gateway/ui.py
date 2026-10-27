"""
Show the gateway as an extra row in the "Addressing" panel of the prefix view.

NetBox has no official hook for adding rows to a core panel, so we wrap that
panel and append our row to its table. If the panel can't be found (e.g. after
a NetBox update), we fall back to a small panel of our own on the right side.
"""
import logging

from django.template.loader import render_to_string

from .constants import GATEWAY_FIELD

logger = logging.getLogger("netbox.plugins.netbox_prefix_gateway")

ADDRESSING_TEMPLATE = "ipam/panels/prefix_addressing.html"
ROW_TEMPLATE = "netbox_prefix_gateway/gateway_row.html"
CARD_TEMPLATE = "netbox_prefix_gateway/gateway_card.html"


def get_gateway(prefix):
    return prefix.cf.get(GATEWAY_FIELD) if prefix else None


def _render_row(context):
    obj = context.get("object")
    return render_to_string(ROW_TEMPLATE, {"gateway": get_gateway(obj)}, request=context.get("request"))


def _wrap_panel(panel):
    original_render = panel.render

    def render(context):
        html = original_render(context)
        idx = html.rfind("</table>")
        if idx == -1:
            return html
        return html[:idx] + _render_row(context) + html[idx:]

    panel.render = render
    panel._prefix_gateway_wrapped = True


def _patch_layout():
    from ipam.views import PrefixView

    layout = getattr(PrefixView, "layout", None)
    if layout is None:
        return False
    for row in layout:
        for column in row:
            for panel in column:
                if getattr(panel, "template_name", None) == ADDRESSING_TEMPLATE:
                    if not getattr(panel, "_prefix_gateway_wrapped", False):
                        _wrap_panel(panel)
                    return True
    return False


def _register_fallback_card():
    from netbox.plugins import PluginTemplateExtension
    from netbox.plugins.registration import register_template_extensions

    class GatewayCard(PluginTemplateExtension):
        models = ["ipam.prefix"]

        def right_page(self):
            return self.render(CARD_TEMPLATE, extra_context={"gateway": get_gateway(self.context["object"])})

    register_template_extensions([GatewayCard])


def install_gateway_row():
    try:
        if _patch_layout():
            return
    except Exception:
        logger.exception("Could not extend the prefix Addressing panel")
    logger.warning("Addressing panel not found, showing gateway in its own panel instead")
    _register_fallback_card()
