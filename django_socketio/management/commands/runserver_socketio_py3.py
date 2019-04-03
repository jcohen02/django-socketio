from django.utils import autoreload
import re
import sys
from datetime import datetime

from django.core.servers.basehttp import get_internal_wsgi_application

from django.conf import settings

from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.runserver import naiveip_re
try:
    from socketio import SocketIOServer
except ImportError:
    from socketio.server import SocketIOServer

from os import environ

from django_socketio.clients import client_end_all
from django_socketio.settings import HOST, PORT

class Command(BaseCommand):

    requires_system_checks = False
    stealth_options = ('shutdown_message',)

    protocol = 'http+ws'

    def handle(self, addrport="", *args, **options):
        if not settings.DEBUG and not settings.ALLOWED_HOSTS:
            raise CommandError('You must set settings.ALLOWED_HOSTS if DEBUG is False.')

        if not addrport:
            self.addr = HOST
            self.port = PORT
        else:
            m = re.match(naiveip_re, options['addrport'])
            if m is None:
                raise CommandError('"%s" is not a valid port number '
                                   'or address:port pair.' % options['addrport'])
            self.addr, _, _, _, self.port = m.groups()
            if not self.port.isdigit():
                raise CommandError("%r is not a valid port number." % self.port)

        # Make the port available here for the path:
        #   socketio_tags.socketio ->
        #   socketio_scripts.html ->
        #   io.Socket JS constructor
        # allowing the port to be set as the client-side default there.
        environ["DJANGO_SOCKETIO_PORT"] = str(self.port)

        if not self.addr:
            self.addr = self.default_addr
        self.run(**options)


    def run(self, **options):
        """Run the server, using the autoreloader if needed."""
        use_reloader = True

        if use_reloader:
            autoreload.run_with_reloader(self.inner_run, **options)
        else:
            self.inner_run(None, **options)

    def inner_run(self, *args, **options):
        # If an exception was silenced in ManagementUtility.execute in order
        # to be raised in the child process, raise it now.
        autoreload.raise_last_exception()

        # 'shutdown_message' is a stealth option.
        shutdown_message = options.get('shutdown_message', '')
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'

        self.stdout.write("Performing system checks...\n\n")
        self.check(display_num_errors=True)
        # Need to check migrations here, so can't use the
        # requires_migrations_check attribute.
        self.check_migrations()
        now = datetime.now().strftime('%B %d, %Y - %X')
        self.stdout.write(now)
        self.stdout.write((
            "Django version %(version)s, using settings %(settings)r\n"
            "Starting development server at %(protocol)s://%(addr)s:%(port)s/\n"
            "Quit the server with %(quit_command)s.\n"
        ) % {
            "version": self.get_version(),
            "settings": settings.SETTINGS_MODULE,
            "protocol": self.protocol,
            "addr": '[%s]' % self.addr,
            "port": self.port,
            "quit_command": quit_command,
        })

        try:
            bind = (self.addr, int(self.port))
            print("\nSocketIOServer running on %s:%s\n" % (bind))
            handler = self.get_handler(*args, **options)
            server = SocketIOServer(bind, handler, resource="socket.io")
            server.serve_forever()
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            client_end_all()
            server.kill()
            sys.exit(0)
    
    def get_handler(self, *args, **options):
        """Return the default WSGI handler for the runner."""
        return get_internal_wsgi_application()
