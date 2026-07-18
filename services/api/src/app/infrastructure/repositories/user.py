from typing import Any
from uuid import UUID

from atlas_core.domain.entities.user import User
from atlas_core.domain.enums.user_role import UserRole

from app.application.ports.user_repository import UserRepository
from app.infrastructure.firestore import BaseRepository, CollectionMapper, FirestoreClient


class UserMapper(CollectionMapper[User]):
    """Mapper to serialize and deserialize User domain entities to/from Firestore."""

    def to_document(self, entity: User) -> dict[str, Any]:
        return {
            "id": str(entity.id),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "version": entity.version,
            "name": entity.name,
            "role": entity.role.value,
            "email": entity.email.lower().strip(),
        }

    def to_entity(self, document_id: str, data: dict[str, Any]) -> User:
        role_str = data.get("role", "fan").lower()
        try:
            role = UserRole(role_str)
        except ValueError:
            role = UserRole.FAN

        return User(
            id=UUID(document_id),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            version=data.get("version", 1),
            name=data["name"],
            role=role,
            email=data["email"],
        )

class FirestoreUserRepository(BaseRepository[User], UserRepository):
    """Firestore implementation of the UserRepository interface."""

    def __init__(self, client: FirestoreClient) -> None:
        super().__init__(client, "users", UserMapper())

    async def get_by_email(self, email: str) -> tuple[User, str] | None:
        """Retrieves a user and their password hash by email address."""
        email_clean = email.strip().lower()
        query = self.collection_ref.where("email", "==", email_clean).limit(1)
        
        snapshots = await query.get()
        if not snapshots:
            return None

        doc = snapshots[0]
        data = doc.to_dict()
        if data is None:
            return None

        user = self.mapper.to_entity(doc.id, data)
        password_hash = data.get("password_hash", "")
        return user, password_hash

    async def save_user(self, user: User, password_hash: str) -> None:
        """Saves a user entity along with their hashed password in Firestore."""
        doc_ref = self.collection_ref.document(str(user.id))
        
        # Check current document for optimistic locking
        snapshot = await doc_ref.get()
        current_data = snapshot.to_dict() if snapshot.exists else None

        if current_data is not None:
            user.version = current_data.get("version", 1) + 1
        else:
            user.version = 1

        serialized_data = self.mapper.to_document(user)
        serialized_data["password_hash"] = password_hash
        serialized_data["version"] = user.version

        await doc_ref.set(serialized_data)
