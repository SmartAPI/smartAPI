from .async_operations_builder import AsyncOperationsBuilder
from .async_operations_builder_with_reasoner import AsyncOperationsBuilderWithReasoner


def async_builder_factory(options, include_reasoner):
    if include_reasoner:
        builder = AsyncOperationsBuilderWithReasoner(options)
    else:
        builder = AsyncOperationsBuilder(options)
    ops = builder.build()
    return ops
