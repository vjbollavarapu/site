"""
Management command to set up default sites
"""
from django.core.management.base import BaseCommand
from apps.core.models import Site


class Command(BaseCommand):
    help = 'Set up default sites for multi-site support'

    def handle(self, *args, **options):
        sites_data = [
            {
                'name': 'oasys360',
                'domain': 'oasys360.com',
                'display_name': 'Oasys360',
                'base_url': 'https://oasys360.com',
                'is_default': True,
            },
            {
                'name': 'heals360',
                'domain': 'heals360.com',
                'display_name': 'Heals360',
                'base_url': 'https://heals360.com',
            },
            {
                'name': 'reliqo',
                'domain': 'reliqo.app',
                'display_name': 'Reliqo',
                'base_url': 'https://reliqo.app',
            },
            {
                'name': 'vcsmy',
                'domain': 'vcsmy.com',
                'display_name': 'VCSMY',
                'base_url': 'https://vcsmy.com',
            },
        ]

        created_count = 0
        updated_count = 0

        for site_data in sites_data:
            site, created = Site.objects.update_or_create(
                name=site_data['name'],
                defaults={
                    'domain': site_data['domain'],
                    'display_name': site_data['display_name'],
                    'base_url': site_data['base_url'],
                    'is_default': site_data.get('is_default', False),
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created site: {site.display_name} ({site.domain})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated site: {site.display_name} ({site.domain})')
                )

        # Ensure only one default site
        default_sites = Site.objects.filter(is_default=True)
        if default_sites.count() > 1:
            # Keep the first one as default, unset others
            first_default = default_sites.first()
            for site in default_sites.exclude(id=first_default.id):
                site.is_default = False
                site.save()
                self.stdout.write(
                    self.style.WARNING(f'  Unset default flag for: {site.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Setup complete! Created: {created_count}, Updated: {updated_count}'
            )
        )

