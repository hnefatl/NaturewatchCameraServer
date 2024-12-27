import dataclasses
import datetime
import subprocess
import time
import json
import requests
import logging

from typing import Callable, TypeVar, Optional

T = TypeVar("T")

LAT_LONG_FILE_PATH = "/home/pi/lat_long.txt"
NATUREWATCH_SERVER_SERVICE_NAME = "python.naturewatch.service"


@dataclasses.dataclass(frozen=True)
class Location:
    lat: float
    long: float

    def __str__(self) -> str:
        return f"({self.lat}, {self.long})"


@dataclasses.dataclass(frozen=True)
class TimeInfo:
    # The times of events for the timezone-aware day on which this object was created,
    # relative to system-local timezone.
    sunrise: datetime.datetime
    sunset: datetime.datetime
    next_1am: datetime.datetime

    def __str__(self) -> str:
        d = {
            "sunrise": self.sunrise.isoformat(),
            "sunset": self.sunset.isoformat(),
            "next_1am": self.next_1am.isoformat(),
        }
        return str(d)

    @staticmethod
    def get_from_web(location: Location):
        today = datetime.datetime.now().astimezone().date()

        url = f"https://api.sunrisesunset.io/json?lat={location.lat}&lng={location.long}&time_format=unix&date={today.year}-{today.month}-{today.day}&timezone=Europe%2FLondon"
        logging.info(f"GETting {url}")
        response = requests.get(url, timeout=60)
        assert response.status_code == 200
        body = json.loads(response.content)
        results = body["results"]
        sunrise = datetime.datetime.fromtimestamp(
            float(results["sunrise"])
        ).astimezone()
        sunset = datetime.datetime.fromtimestamp(float(results["sunset"])).astimezone()

        # For some reason, the date returned by the API is a day old, but the time is correct.
        sunrise = sunrise.replace(year=today.year, month=today.month, day=today.day)
        sunset = sunset.replace(year=today.year, month=today.month, day=today.day)

        return TimeInfo(
            sunrise=sunrise,
            sunset=sunset,
            next_1am=(
                datetime.datetime.combine(
                    date=today, time=datetime.time(hour=1)
                ).astimezone()
                + datetime.timedelta(days=1)
            ),
        )

    @staticmethod
    def default() -> "TimeInfo":
        today = datetime.datetime.now().astimezone().date()
        # Assume 6am until 9pm sunup
        return TimeInfo(
            sunrise=datetime.datetime.combine(
                date=today, time=datetime.time(hour=6)
            ).astimezone(),
            sunset=datetime.datetime.combine(
                date=today, time=datetime.time(hour=21)
            ).astimezone(),
            next_1am=(
                datetime.datetime.combine(
                    date=today, time=datetime.time(hour=1)
                ).astimezone()
                + datetime.timedelta(days=1)
            ),
        )


def get_location_from_file() -> Location:
    with open(LAT_LONG_FILE_PATH) as f:
        return Location(lat=float(f.readline()), long=float(f.readline()))


def retry(
    times: int,
    delay_s: float,
    f: Callable[[], T],
) -> Optional[T]:
    for i in range(0, times):
        try:
            return f()
        except Exception as e:
            logging.warning(f"Failed call {i}, retrying in {delay_s}s: exception {e}")
            time.sleep(delay_s)
    return None


def sleep_until(t: datetime.datetime):
    delta = t - datetime.datetime.now().astimezone()
    logging.info(f"Sleeping until {t}")
    time.sleep(delta.total_seconds())


def set_service_state(start: bool):
    args = [
        "systemctl",
        "start" if start else "stop",
        NATUREWATCH_SERVER_SERVICE_NAME,
    ]
    logging.info(f"Running {args}")
    result = subprocess.run(args, stdout=subprocess.PIPE)
    logging.log(
        msg=f"Exited with code {result.returncode}",
        level=logging.INFO if result.returncode == 0 else logging.ERROR,
    )


def main():
    logging.getLogger().setLevel(logging.INFO)

    location = get_location_from_file()
    logging.info(f"Location: {location}")

    while True:
        sun_info = retry(5, 120, lambda: TimeInfo.get_from_web(location))
        logging.info(f"Sun info: {sun_info}")
        if sun_info is None:
            sun_info = TimeInfo.default()
            logging.warning(f"Failed to get sun_info, using default: {sun_info}")

        if not (
            sun_info.sunrise < sun_info.sunset and sun_info.sunset < sun_info.next_1am
        ):
            logging.error(f"Unexpected ordering of time events: {sun_info}")

        if datetime.datetime.now().astimezone() < sun_info.sunrise:
            set_service_state(start=False)
            sleep_until(sun_info.sunrise)
        if datetime.datetime.now().astimezone() < sun_info.sunset:
            set_service_state(start=True)
            sleep_until(sun_info.sunset)
        # Wait until the next day before fetching the next sunrise/set information.
        if datetime.datetime.now().astimezone() < sun_info.next_1am:
            # Make sure shutdown if this program is started after sunset.
            set_service_state(start=False)
            sleep_until(sun_info.next_1am)


if __name__ == "__main__":
    main()
