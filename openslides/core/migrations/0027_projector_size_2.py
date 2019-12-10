# Generated by Finn Stutzenstein on 2019-11-22 11:42

from django.db import migrations


def calculate_aspect_ratios(apps, schema_editor):
    """
    Assignes every projector one aspect ratio of the ones, that OS
    supported until this migration. If no matching ratio was found, the
    default of 16:9 is assigned.
    """
    Projector = apps.get_model("core", "Projector")
    ratio_environment = 0.05
    aspect_ratios = {
        4 / 3: (4, 3),
        16 / 9: (16, 9),
        16 / 10: (16, 10),
        30 / 9: (30, 9),
    }

    for projector in Projector.objects.all():
        projector_ratio = projector.width / projector.height
        ratio = (16, 9)  # default, if no matching aspect ratio was found.
        # Search ratio, that fits to the projector_ratio. Take first one found.
        for value, _ratio in aspect_ratios.items():
            if (
                value >= projector_ratio - ratio_environment
                and value <= projector_ratio + ratio_environment
            ):
                ratio = _ratio
                break
        projector.aspect_ratio_numerator = ratio[0]
        projector.aspect_ratio_denominator = ratio[1]
        projector.save(skip_autoupdate=True)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0026_projector_size_1"),
    ]

    operations = [
        migrations.RunPython(calculate_aspect_ratios),
    ]