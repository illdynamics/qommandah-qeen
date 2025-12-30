class GameException(Exception):
    """Base exception for all game-related errors."""
    pass

class ResourceException(GameException):
    """Raised when resource loading fails."""
    pass

class LevelException(GameException):
    """Raised when level data is invalid or cannot be loaded."""
    pass

class PhysicsException(GameException):
    """Raised when physics simulation encounters an error."""
    pass

class CollisionException(GameException):
    """Raised when collision detection fails."""
    pass

class StateException(GameException):
    """Raised when an invalid state transition is attempted."""
    pass

class InputException(GameException):
    """Raised when input handling fails."""
    pass

class RenderException(GameException):
    """Raised when rendering fails."""
    pass

class AudioException(GameException):
    """Raised when audio playback fails."""
    pass

class NetworkException(GameException):
    """Raised when network communication fails."""
    pass

class ConfigurationException(GameException):
    """Raised when configuration is invalid or missing."""
    pass

class SaveException(GameException):
    """Raised when save/load operations fail."""
    pass

class ValidationException(GameException):
    """Raised when data validation fails."""
    pass

class TimeoutException(GameException):
    """Raised when an operation times out."""
    pass

class NotImplementedException(GameException):
    """Raised when a feature is not yet implemented."""
    pass

class OutOfBoundsException(GameException):
    """Raised when an object moves outside valid boundaries."""
    pass

class InsufficientResourcesException(GameException):
    """Raised when required resources are not available."""
    pass

class InvalidOperationException(GameException):
    """Raised when an operation is invalid in the current context."""
    pass

class InvalidDoorStateError(GameException):
    """Raised when door state is invalid."""
    pass

class ResourceLoadError(GameException):
    """Raised when resource loading fails."""
    pass

class InvalidStateError(GameException):
    """Raised when an invalid state is encountered."""
    pass