from django.db import migrations

FIELD_NAME = "gateway"


def create_field(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    CustomField = apps.get_model("extras", "CustomField")

    if CustomField.objects.filter(name=FIELD_NAME).exists():
        # Don't touch a field the user created themselves
        return

    prefix_ct, _ = ContentType.objects.get_or_create(app_label="ipam", model="prefix")
    ip_ct, _ = ContentType.objects.get_or_create(app_label="ipam", model="ipaddress")

    field = CustomField.objects.create(
        name=FIELD_NAME,
        label="Gateway",
        type="object",
        related_object_type_id=ip_ct.pk,
        # Only offer IPs inside the prefix being edited
        related_object_filter={"parent": "$prefix"},
        description="Default gateway of this prefix",
        required=False,
        # Shown in the Addressing panel by the plugin, not in the Custom Fields panel
        ui_visible="hidden",
        ui_editable="yes",
        weight=100,
    )
    field.object_types.add(prefix_ct.pk)


def delete_field(apps, schema_editor):
    CustomField = apps.get_model("extras", "CustomField")
    CustomField.objects.filter(name=FIELD_NAME, type="object").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0121_customfield_related_object_filter"),
        ("ipam", "0001_squashed"),
    ]

    operations = [
        migrations.RunPython(create_field, delete_field),
    ]
