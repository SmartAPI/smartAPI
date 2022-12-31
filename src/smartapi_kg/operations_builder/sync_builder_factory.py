from .sync_operations_builder import SyncOperationsBuilder
from .sync_operations_builder_with_reasoner import SyncOperationsBuilderWithReasoner


def sync_builder_factory(options, include_reasoner, smartapi_path, predicates_path):
    if include_reasoner:
        builder = SyncOperationsBuilderWithReasoner(options, smartapi_path, predicates_path)
    else:
        builder = SyncOperationsBuilder(options, smartapi_path)

    ops = builder.build()
    return ops
