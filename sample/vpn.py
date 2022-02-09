import os, logging, pexpect


class Session:
    def __init__(self, path, created, config, status):
        self.path = path
        self.created = created
        self.config = config.split('/')[-1].split('(Config')[0]
        self.status = status

    def __str__(self):
        return 'Session[Config: ' + self.config + \
            '\n\tCreated: ' + self.created + \
            '\n\tStatus: ' + self.status + ']\n'


class OpenVpn:
    def __init__(self, creds=None):
        self.creds = creds
        self.config = creds.profile.ovpn
        self.config_name = str(self.config).split('/')[-1]
        self.sessions: list[Session] = []

    def stopAll(self):
        if not self.sessions: self.sessions = OpenVpn.parseSessions()
        if self.sessions:
            for s in self.sessions:
                if s.config.strip() == self.config_name.strip():
                    self.stop(s.path)

    def start(self):
        if not self.sessions: self.sessions = OpenVpn.parseSessions()
        if self.sessions:
            for s in self.sessions:
                if 'Client connected' in s.status.strip():
                    logging.info("🟢 Client already connected at: " + s.created)
                    return
        command = f'openvpn3 session-start --config {self.config}'
        logging.info("🟢 Turning on VPN 🟢")
        output = pexpect.run(command, 5, False, self.creds.getExpectedEvents()).decode("utf-8")
        logging.info(output)

    def stop(self, path):
        command = f'openvpn3 session-manage --session-path {path} --disconnect'
        logging.info("🔴 Turning off VPN 🔴")
        output = os.popen(command).read()
        logging.info(output)

    @staticmethod
    def parseSessions() -> list[Session]:
        command = 'openvpn3 sessions-list'
        output = os.popen(command).readlines()
        tmp_path = tmp_crtd = tmp_cfg = tmp_stat = None
        parse = lambda line: line.strip().split(': ')[1]
        sessions = list()
        for line in output:
            if 'Path:' in line: tmp_path = parse(line)
            elif 'Created' in line: tmp_crtd = parse(line).split(' 2022')[0]
            elif 'Config name' in line: tmp_cfg = parse(line)
            elif 'Status' in line:
                tmp_stat = parse(line)
                sessions.append(Session(tmp_path,tmp_crtd,tmp_cfg,tmp_stat))
        return sessions

    @staticmethod
    def printSessions():
        [logging.info(str(s)) for s in OpenVpn.parseSessions()]
