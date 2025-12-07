"""
Management command to set up admin permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Set up admin permission groups'

    def handle(self, *args, **options):
        # Create admin groups
        groups_config = {
            'Viewers': {
                'description': 'View-only access to all models',
                'permissions': ['view'],
            },
            'Editors': {
                'description': 'Can view and edit all models',
                'permissions': ['view', 'add', 'change'],
            },
            'Exporters': {
                'description': 'Can view and export data',
                'permissions': ['view', 'export'],
            },
            'Managers': {
                'description': 'Full access including delete',
                'permissions': ['view', 'add', 'change', 'delete'],
            },
        }
        
        # Get all content types for our apps
        app_labels = [
            'contacts',
            'waitlist',
            'leads',
            'newsletter',
            'analytics',
            'gdpr',
        ]
        
        content_types = ContentType.objects.filter(app_label__in=app_labels)
        
        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Group already exists: {group_name}'))
            
            # Add permissions based on group type
            permissions_to_add = []
            
            for content_type in content_types:
                model_name = content_type.model
                
                for perm_type in config['permissions']:
                    if perm_type == 'view':
                        codename = f'view_{model_name}'
                    elif perm_type == 'add':
                        codename = f'add_{model_name}'
                    elif perm_type == 'change':
                        codename = f'change_{model_name}'
                    elif perm_type == 'delete':
                        codename = f'delete_{model_name}'
                    elif perm_type == 'export':
                        # Export is a custom permission - would need to be defined in models
                        continue
                    else:
                        continue
                    
                    try:
                        perm = Permission.objects.get(
                            content_type=content_type,
                            codename=codename
                        )
                        permissions_to_add.append(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'Permission not found: {codename}')
                        )
            
            # Add permissions to group
            group.permissions.set(permissions_to_add)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Added {len(permissions_to_add)} permissions to {group_name}'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('Admin permissions setup complete!'))

