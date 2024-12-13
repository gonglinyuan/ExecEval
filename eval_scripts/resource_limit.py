from dataclasses import dataclass, fields


@dataclass(kw_only=True)
class ResourceLimits:
    core: int = 0  # RLIMIT_CORE
    fsize: int = 0  # RLIMIT_FSIZE
    sigpending: int = 0  # RLIMIT_SIGPENDING
    nofile: int = 4  # RLIMIT_NOFILE
    msgqueue: int = 0  # RLIMIT_MSGQUEUE
    rtprio: int = 0  # RLIMIT_RTPRIO
    cpu: int = 2  # RLIMIT_CPU, CPU time, in seconds.
    nproc: int = 1  # RLIMIT_NPROC
    _as: int = 2 * 1024 ** 3  # RLIMIT_AS set to 2GB by default
    locks: int = 0  # RLIMIT_LOCKS

    def fields(self):
        for field in fields(self):
            yield field.name


if __name__ == "__main__":
    limits = ResourceLimits()
    prlimit_str = " ".join(
        f"--{field.name[1:] if field.name.startswith('_') else field.name}={getattr(limits, field.name)}"
        for field in fields(limits)
    )
    print(prlimit_str)
