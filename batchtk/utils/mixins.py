from abc import ABC, abstractmethod
from typing import Any
class StateMixin(ABC):
    """
    A mixin for classes that manage transient state (like file handles,
    network connections, or non-serializable objects).

    This provides a robust, fail-fast contract for serialization
    and state management.

    Note -- all attributes and methods prepended with _
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

    @property
    @abstractmethod
    def _state_config(self) -> dict:
        """
        [Abstract Property] Subclass must define this as a class
        or instance attribute. It must be a list or tuple of
        attribute names (strings) that should not be pickled.
        """
        # abstract property, here to signal importance.
        # additional RTC in __getstate__:
        raise NotImplementedError

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

    def _reset_state(self):
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

    def _recreate_state_from_config(self):
        """
        Populates all transient attributes using a two-pass build
        to support shared component references.
        """
        if not hasattr(self, 'state_config'):
            raise TypeError(f"{self.__class__.__name__} must define 'state_config' in its __init__.")

        # This cache will hold shared instances (from _components_)
        # AND literal values for referencing.
        self._built_components_cache = {}

        # --- Pass 1: Process Shared Components & Literals ---
        component_specs = self.state_config.get('_components_', {})
        for name, spec in component_specs.items():
            # Build the component and store it in the cache
            self._built_components_cache[name] = self._build_from_spec(spec)

        # --- Pass 2: Build Transient Attributes ---
        if not hasattr(self, '_transient_attributes'):
            raise TypeError(...)

        for attr in self._transient_attributes:
            spec = self.state_config.get(attr)
            setattr(self, attr, self._build_from_spec(spec))

        # Clean up the cache, it's no longer needed
        del self._built_components_cache

    def _build_from_spec(self, spec: Any) -> Any:
        """
        Recursively builds an object from a "spec",
        now with support for references.
        """

        # --- 1. Check for Reference ---
        # A "reference spec" is a dict with a '_ref_' key
        if isinstance(spec, dict) and '_ref_' in spec:
            ref_name = spec['_ref_']
            try:
                # Look up the already-built instance from the cache
                return self._built_components_cache[ref_name]
            except KeyError:
                raise ValueError(f"Invalid reference. Component '{ref_name}' is not defined in '_components_'.")

        # --- 2. Check for Constructor ---
        # A "build spec" is a dict containing a '_constructor_' key
        if isinstance(spec, dict) and '_constructor_' in spec:
            constructor = spec['_constructor_']
            kwargs_spec = spec.get('_kwargs_', {})

            final_kwargs = {}
            for key, value_spec in kwargs_spec.items():
                # RECURSIVE CALL
                final_kwargs[key] = self._build_from_spec(value_spec)

            return constructor(**final_kwargs)

        # --- 3. Base Case: Literal Value ---
        # The spec is a literal (e.g., a string, int, or None)
        return spec