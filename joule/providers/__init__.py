import logging

from abc import ABC, abstractmethod
from time import sleep
from typing import Iterator, Optional

from joule.events import Events, Event


class BaseProvider(ABC):
    """
    Base Provider class.

    These methods are required in order to operate a provider's scale group,
    based on the application object this consumes.

    It is expected these inheriting provider classes will either use an
    existing API library, or call the provider's API via HTTP requests.
    """

    @abstractmethod
    def __init__(self, *applications: object) -> None:
        """
        :param: application: BaseApplication
        """
        self.applications: tuple = applications
        self._tag_enrolled: dict = {"Key": "joule:enrolled", "Value": "1"}

    @abstractmethod
    def mark_essential(self) -> None:
        """
        Tell the provider that this instance should be protected against
        termination during a scale event.

        :return: None
        """

    @abstractmethod
    def mark_enrolled(self) -> None:
        """
        Mark this instance as being enrolled in the application's cluster.

        :return: None
        """

    @abstractmethod
    def is_enrolled(self) -> bool:
        """
        Return whether or not this instance has been enrolled into the
        application's cluster.

        :return: Boolean
        """

    @abstractmethod
    def get_events_from_message_queue(self) -> Iterator[Event]:
        """
        Read messages from the provider's message queue and parse the relevant
        scaling group events.  Transform parsed events into Even objects to be
        yielded into the main loop.

        :return: Event
        """

    @abstractmethod
    def send_join_to_message_queue(
        self, application: object, event: Event, payload: dict
    ) -> None:
        """
        Write the authentication payload generated by any existing instance
        back onto the provider's message queue.  This will then be consumed
        by a joining instance in order to authenticate into the application's
        cluster.

        :param application: BaseApplication
        :param event: Event
        :param payload: Dictionary
        :return: None
        """

    def loop(self) -> None:
        """
        Loop indefinitely, check for events and act upon them.

        This is the recommended use case, but can be overloaded to be more
        provider specific.

        :return: None
        """
        while True:

            logging.debug("Loop")
            self.mark_essential()

            for event in self.get_events_from_message_queue():
                if event.event is Events.JOIN:
                    logging.info("JOIN event.")
                    for app in self.applications:
                        if event.application == app:
                            app.join(self, event)
                    self.mark_enrolled()

                elif event.event is Events.LAUNCH:
                    logging.info("LAUNCH event.")
                    for app in self.applications:
                        app.launch(self, event)

                elif event.event is Events.TERMINATE:
                    logging.info("TERMINATE event.")
                    for app in self.applications:
                        app.terminate(self, event)

            sleep(5)
            continue
