from django.core.management.base import BaseCommand, CommandError

from core.models import CollectorAgent, Station
from core.services import get_or_create_local_collector


class Command(BaseCommand):
    help = "Create the tokenless local collector and optionally assign stations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all-active",
            action="store_true",
            help="Assign every active station to the local collector.",
        )
        parser.add_argument(
            "--station",
            action="append",
            dest="stations",
            help="Station UUID to assign. Repeat this option for multiple stations.",
        )

    def handle(self, *args, **options):
        if options["all_active"] and options["stations"]:
            raise CommandError("Use either --all-active or --station, not both.")

        collector = get_or_create_local_collector()
        if options["all_active"]:
            stations = Station.objects.filter(is_active=True)
            collector.assigned_stations.add(*stations)
        elif options["stations"]:
            stations = Station.objects.filter(id__in=options["stations"], is_active=True)
            found_ids = {str(station.id) for station in stations}
            missing = set(options["stations"]) - found_ids
            if missing:
                raise CommandError(f"Unknown or inactive station UUID(s): {', '.join(sorted(missing))}")
            collector.assigned_stations.add(*stations)

        assigned = collector.assigned_stations.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Local collector ready: {collector.id}; assigned active stations: {assigned}"
            )
        )
