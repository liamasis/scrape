import json
import random
import time

from swarm.scraper.utils import generate_uuid, generate_android_device_id

USER_AGENT_BASE = (
    "Instagram {app_version} "
    "Android ({android_version}/{android_release}; "
    "{dpi}; {resolution}; {manufacturer}; "
    "{model}; {device}; {cpu}; {locale}; {version_code})"
)

APP_VERSIONS = ['245.0.0.18.108', '245.0.0.6.108', '244.1.0.19.110', '240.2.0.18.107', '243.0.0.16.111', '235.0.0.21.107']
ANDROID_RELEASE_VERSIONS = [(31, '12'), (30, '11'), (29, '10')]
DEVICES = [
    ('450dpi', '1080x2190', 'samsung',			'SM-G998B',			'p3s',			'exynos2100', 			'384108444'),
    ('420dpi', '1080x2200', 'samsung',			'SM-G988W',			'z3q', 			'qcom', 				'385416228'),
    ('440dpi', '1080x2190', 'Xiaomi', 			'M2012K11G',		'haydn', 		'qcom', 				'385416228'),
    ('420dpi', '1080x2094', 'samsung', 			'SM-G950F',			'dreamlte', 	'samsungexynos8895', 	'366008860'),
    ('420dpi', '1080x2115', 'samsung', 			'SM-S908E',			'b0q', 			'qcom', 				'384108444'),
    ('560dpi', '1440x2934', 'Google/google', 	'Pixel 6 Pro',		'raven',		'raven', 				'364619248'),
    ('440dpi', '1080x2160', 'Google/google', 	'Pixel 4a',			'sunfish', 		'sunfish', 				'366008860'),
    ('420dpi', '1080x2241', 'OnePlus', 			'IN2023',			'OnePlus8Pro', 	'qcom', 				'364619241')
]


class DeviceSettings:
    app_version: str
    android_version: int
    android_release: int
    dpi: str
    resolution: str
    manufacturer: str
    device: str
    model: str
    cpu: str
    version_code: int

    def __init__(self, app_version: str, android_version: int, android_release: int, dpi: str, resolution: str, manufacturer: str, device: str, model: str, cpu: str, version_code: int) -> None:
        self.app_version = app_version
        self.android_version = android_version
        self.android_release = android_release
        self.dpi = dpi
        self.resolution = resolution
        self.manufacturer = manufacturer
        self.device = device
        self.model = model
        self.cpu = cpu
        self.version_code = version_code


    def to_user_agent(self, locale):
        return USER_AGENT_BASE.format(locale=locale, **self.__dict__)


class UUIDs:
    phone_id: str
    uuid: str
    client_session_id: str
    advertising_id: str
    android_device_id: str
    request_id: str
    tray_session_id: str

    def __init__(self) -> None:
        self.phone_id = generate_uuid()
        self.uuid = generate_uuid()
        self.client_session_id = generate_uuid()
        self.advertising_id = generate_uuid()
        self.android_device_id = generate_android_device_id()
        self.request_id = generate_uuid()
        self.tray_session_id = generate_uuid()


class Settings:
    uuids: UUIDs
    mid: str
    ig_u_rur: {}
    ig_www_claim: {}
    authorization_data: {}
    cookies: {}
    last_login: float
    device_settings: DeviceSettings
    user_agent: str
    country: str
    country_code: int
    locale: str
    timezone_offset: int

    def __init__(self) -> None:
        device_settings, user_agent = generate_device_settings()

        self.uuids = UUIDs()
        self.mid = None
        self.ig_u_rur = None
        self.ig_www_claim = None
        self.authorization_data = None
        self.cookies = {}
        self.last_login = None
        self.device_settings = device_settings
        self.user_agent = user_agent
        self.country = 'AU'
        self.country_code = 61
        self.locale = 'en_AU'
        self.timezone_offset = 10 * 3600

    def to_json(self):
        return json.dumps(self, default=lambda o: getattr(o, '__dict__', str(o)))


def generate_device_settings():
    app_version = random.choice(APP_VERSIONS)
    android_version, release_version = random.choice(ANDROID_RELEASE_VERSIONS)
    dpi, resolution, manufacturer, device, model, cpu, version_code = random.choice(DEVICES)
    locale = 'en_AU'
    device = DeviceSettings(app_version, android_version, release_version, dpi, resolution, manufacturer, device, model, cpu, version_code)
    return device, device.to_user_agent(locale)


if __name__ == '__main__':
    a = Settings()
    print(a.to_json())
