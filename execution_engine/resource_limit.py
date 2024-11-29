from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass(kw_only=True)
class ResourceLimits:
    cpu: int = 2  # RLIMIT_CPU, CPU time, in seconds.
    _as: int = 2 * 1024 ** 3  # RLIMIT_AS set to 2GB by default

    def fields(self):
        for field in fields(self):
            yield field.name

    def update(self, other: ResourceLimits):
        for field in fields(other):
            setattr(self, field.name, getattr(other, field.name))


if __name__ == "__main__":
    limits = ResourceLimits()
    other = ResourceLimits(cpu=1, _as=2)
    limits.update(other)
    prlimit_str = " ".join(
        f"--{field.name[1:] if field.name.startswith('_') else field.name}={getattr(limits, field.name)}"
        for field in fields(limits)
    )
    print(prlimit_str)
