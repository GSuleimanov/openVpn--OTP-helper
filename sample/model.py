import os, pathlib, logging, pexpect, utils


class Pool:
    @staticmethod
    def get_profiles():
        return [Profile(name) for name in Pool.get_profile_names()]

    @staticmethod
    def get_sessions():
        return OpenVpn.parse_sessions()

    @staticmethod
    def get_profile_names():
        return list(c.name[:-5] for c in Profile.vpnConfigsFolder.glob('**/*.ovpn'))


class Profile:
    parentFolder = pathlib.Path(__file__).parents[1]
    vpnConfigsFolder = parentFolder / 'vpn_configs'

    def __init__(self, name):
        self.name = name
        self.ini = next(Profile.vpnConfigsFolder.glob(f'**/{name}.ini'))
        self.ovpn = next(Profile.vpnConfigsFolder.glob(f'**/{name}.ovpn'))
        self.credentials = Credentials(self.ini)

    @staticmethod
    def get_all_profiles():
        return list(c.name[:-4] for c in Profile.vpnConfigsFolder.glob('**/*.ini'))


class Credentials:
    def __init__(self, ini):
        config = utils.parse_config(ini)
        self.user = config.get('Credentials', 'USER')
        self.pswd = config.get('Credentials', 'PASS')
        self.secret = config['Credentials']['OTP_SECRET']

    def get_expected_events(self):
        return {'.*Auth User name:.*': self.user + '\n',
                '.*Auth Password:.*': self.pswd + utils.get_otp_code(self.secret) + '\n'}


class OpenVpn:
    available_commands = 'ls', 'on', 'off'

    @staticmethod
    def do(command, profile=None):
        if command == 'ls': OpenVpn.print_sessions()
        elif command == 'on': OpenVpn.start(profile)
        elif command == 'off': OpenVpn.stop_all(profile)

    @staticmethod
    def start(profile):
        sessions = OpenVpn.parse_sessions()
        if sessions and any('Client connected' in s.status.strip() for s in sessions if profile.name in s.config):
            logging.info("Client already connected")
            return
        command = f'openvpn3 session-start --config {profile.ovpn}'
        logging.info("Turning on VPN")
        output = pexpect.run(command, 5, False, profile.credentials.get_expected_events()).decode("utf-8")
        logging.info(output)

    @staticmethod
    def stop(path):
        command = f'openvpn3 session-manage --session-path {path} --disconnect'
        logging.info("Turning off VPN")
        output = os.popen(command).read()
        logging.info(output)

    @staticmethod
    def stop_all(profile):
        [OpenVpn.stop(s.path) for s in OpenVpn.parse_sessions() if profile.name in s.config]

    @staticmethod
    def parse_sessions():
        command = 'openvpn3 sessions-list'
        output = os.popen(command).readlines()
        tmp_path = tmp_crtd = tmp_cfg = tmp_stat = None
        parse = lambda line: line.strip().split(': ')[1]
        sessions = list()
        for line in output:
            if 'Path:' in line:
                tmp_path = parse(line)
            elif 'Created' in line:
                tmp_crtd = parse(line).split(' 2022')[0]
            elif 'Config name' in line:
                tmp_cfg = parse(line)
            elif 'Status' in line:
                tmp_stat = parse(line)
                sessions.append(Session(tmp_path, tmp_crtd, tmp_cfg, tmp_stat))
        return sessions

    @staticmethod
    def print_sessions():
        [logging.info(str(s)) for s in OpenVpn.parse_sessions()]


class Session:
    def __init__(self, path, created, config, status):
        self.path = path
        self.created = created
        self.config = config.split('/')[-1].split('(Config')[0].strip()
        self.status = status

    def __str__(self):
        return f'Session(Config={self.config}; Created={self.created}; Status={self.status})'