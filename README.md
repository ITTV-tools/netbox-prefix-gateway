# NetBox Prefix Gateway

Adds an optional **Gateway** field to IPAM prefixes.

- The gateway is an IP address from NetBox, selected in the normal prefix edit form.
  The dropdown only offers IPs inside the prefix.
- Shown as an extra row in the prefix's **Addressing** panel.
- Validation on save (UI and API): the gateway must be inside the prefix, in the same
  VRF, and (IPv4 < /31) not the network or broadcast address.
- Works with filters, bulk edit, CSV import and the REST API (`custom_fields.gateway`).

## How it works

The value is stored in a custom field named `gateway` (type *Object → IP address*),
which the plugin creates in its first migration. The field is hidden from the generic
*Custom Fields* panel because the plugin shows it in the Addressing panel instead.
If a custom field named `gateway` already exists, the migration leaves it untouched.

If NetBox's Addressing panel can't be found (e.g. after a NetBox UI change), the
gateway is shown in a small panel of its own on the right side instead.

## Install

```bash
pip install git+https://github.com/ITTV-tools/netbox-prefix-gateway.git
```

```python
# configuration.py
PLUGINS = ["netbox_prefix_gateway"]
```

```bash
python manage.py migrate
```

## Uninstall

`python manage.py migrate netbox_prefix_gateway zero` removes the custom field
**and all stored gateway values**. Just removing the plugin from `PLUGINS` keeps the
field and its data (it then shows up in the normal Custom Fields panel).

## Compatibility

Tested with NetBox 4.7.

## License

Apache License 2.0, see [LICENSE](LICENSE).
