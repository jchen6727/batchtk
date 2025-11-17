from abc import ABC, abstractmethod
from typing import Any
class StateMixin(ABC):
    """
    A mixin for classes that manage transient state (like file handles,
    network connections, or non-serializable objects).

    This provides a robust, fail-fast contract for serialization
    and state management.
    """

    @property
    @abstractmethod
    def _state_attributes(self) -> list[str] | tuple[str, ...]:
        """
        [Abstract Property] Subclass must define this as a class
        or instance attribute. It must be a list or tuple of
        attribute names (strings) that should not be pickled.
        """
        # abstract property, here to signal importance.
        # additional RTC in __getstate__:
        raise NotImplementedError

    @abstractmethod
    def _create_state_from_config(self):
        """
        [Abstract Method] Subclass must implement this.

        This method is responsible for building
        attributes after deserialization or during a state reset.
        It should use the persistent config (e.con, self.state_config)
        to re-create any transient attributes.
        """
        pass

    def __getstate__(self):
        """Prepares the object for pickling by removing transient state."""
        state = self.__dict__.copy()

        # We still check for _transient_attributes at runtime,
        # as it's an attribute, not a method.
        if not hasattr(self, '_state_attributes'):
            raise TypeError(
                f"{self.__class__.__name__} must define a '_state_attributes' list to use StateMixin."
            )

        for attr in self._state_attributes:
            state.pop(attr, None)
        return state

    def __setstate__(self, state):
        """Restores the object after unpickling and rebuilds transient state."""
        self.__dict__.update(state)
        self._create_state_from_config()

    def reset_state(self):
        """
        Public method to forcibly close and rebuild the object's
        transient state.
        """
        # 'close_state' remains an OPTIONAL part of the contract.
        # We check for it with hasattr.
        if hasattr(self, 'close_state'):
            self.close_state()

        # '_recreate_state_from_config' is REQUIRED.
        # We can call it knowing it exists.
        self._create_state_from_config()

    def _set_attrs(self, attrs_dict:dict[str, Any]):
        if not hasattr(self, '_state_attributes'):
            raise TypeError(
                f"{self.__class__.__name__} must define a '_state_attributes' list to use StateMixin."
            )
        for attr, value in attrs_dict.items():
            if attr not in self._state_attributes:
                raise ValueError(f"{attr} is not a valid attribute in self._state_attributes")
            setattr(self, attr, value)

    def _create_state_from_config(self):
        """
        Default implementation for recreating transient state.

        This method relies on two attributes being set by the subclass:
        1. self._transient_attributes
        2. self.state_config

        This method is responsible for building
        attributes after deserialization or during a state reset.
        It should use the persistent config (e.con, self.state_config)
        to re-create any transient attributes.
        """

        if not hasattr(self, '_transient_attributes'):
            raise TypeError(f"{self.__class__.__name__} must define '_transient_attributes'.")
        if not hasattr(self, '_state_config'):
            raise TypeError(f"{self.__class__.__name__} must define '_state_config' in its __init__.")

        for attr in self._transient_attributes:
            # Get the value/constructor from the config
            val = self.state_config.get(attr)

            if callable(val):
                # It's a constructor (e.g., CustomFS)
                # Look for associated kwargs (e.g., 'fs_kwargs')
                kwargs = self.state_config.get(f"{attr}_kwargs", {})
                # Create the instance
                setattr(self, attr, val(**kwargs))
            else:
                # It's a simple value (or None)
                setattr(self, attr, val)
