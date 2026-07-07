class CollectionResolver:
    """Resolves Firestore collection references based on class type or name."""

    @staticmethod
    def resolve(model_type: type | str) -> str:
        """Returns the Firestore collection name for a given class or string name."""
        name = model_type if isinstance(model_type, str) else model_type.__name__
        name_lower = name.lower()
        if name_lower.endswith("state"):
            return "operational_states"
        if name_lower.endswith("y"):
            return name_lower[:-1] + "ies"
        if name_lower.endswith("s"):
            return name_lower
        return name_lower + "s"
