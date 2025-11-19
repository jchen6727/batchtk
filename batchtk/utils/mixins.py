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

    def _create_state_from_config(self):
        """
        Populates all state attributes. The build order
        is resolved lazily by _get_component.
        """
        if not hasattr(self, '_state_config'):
            raise TypeError(f"{self.__class__.__name__} must define 'state_config' in its __init__.")
        if not hasattr(self, '_state_attributes'):
            raise TypeError(...)

        # Initialize the cache for this build cycle
        self._component_cache = {}

        # There is no "Pass 1" anymore. We just build the
        # main attributes. Shared components will be built
        # on-demand when they are first referenced.
        for attr in self._state_attributes:
            spec = self._state_config.get(attr)
            setattr(self, attr, self._build_from_spec(spec))

        # Clean up the cache
        del self._component_cache

    def _get_component(self, name: str) -> Any:
        """
        Resolves a component reference.

        This is the core of the on-demand logic. It checks the cache,
        and if the component isn't built yet, it finds its spec
        and builds it recursively *before* returning it.
        """
        # 1. Check if already built and cached
        if name in self._component_cache:
            return self._component_cache[name]

        # 2. Not in cache. Find its "spec" in the config.
        if '_components_' not in self._state_config or \
                name not in self._state_config['_components_']:
            raise ValueError(f"Invalid reference. Component '{name}' is not defined in '_components_'.")

        spec = self._state_config['_components_'][name]

        # 3. Build it from the spec (this might trigger other
        #    recursive calls to _get_component)
        instance = self._build_from_spec(spec)

        # 4. Cache the instance
        self._component_cache[name] = instance

        return instance

    def _build_from_spec(self, spec: Any) -> Any:
        """
        Recursively builds an object from a "spec".
        """

        # --- 1. Check for Reference ---
        if isinstance(spec, dict) and '_ref_' in spec:
            # Delegate to the component resolver
            return self._get_component(spec['_ref_'])

        # --- 2. Check for Constructor ---
        if isinstance(spec, dict) and '_constructor_' in spec:
            constructor = spec['_constructor_']
            kwargs_spec = spec.get('_kwargs_', {})

            final_kwargs = {}
            for key, value_spec in kwargs_spec.items():
                # RECURSIVE CALL to build the arguments
                final_kwargs[key] = self._build_from_spec(value_spec)

            return constructor(**final_kwargs)

        # --- 3. Base Case: Literal Value ---
        return spec