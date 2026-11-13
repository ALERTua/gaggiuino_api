"""The health of the machine: the answer of `GET /api/health`."""

from dataclasses import dataclass

from .base import Model, api


@dataclass(frozen=True, kw_only=True)
class Health(Model):
    """The answer of the health check. The machine reports `ok` when it works."""

    status: str = api("status")

    @property
    def ok(self) -> bool:
        """Whether `status` is `ok`."""
        return self.status == "ok"
