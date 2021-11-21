from pydoc_fork.custom_types import TypeLike


def docother(
    the_object: TypeLike,
    name: str = "",  # Null safety,
    # mod: Optional[str] = None,
    # *ignored,
) -> str:
    """Produce HTML documentation for a data object."""
    lhs = name and "<strong>%s</strong> = " % name or ""
    return lhs + repr(the_object)
