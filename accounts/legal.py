
from .models import LegalDocument


def get_active_legal_documents():
    documents = {}

    for document_type in ("terms", "privacy"):
        document = (
            LegalDocument.objects
            .filter(
                document_type=document_type,
                is_active=True,
            )
            .order_by("-updated_at")
            .first()
        )

        if document is None:
            raise ValueError(
                f"No active legal document configured for "
                f"'{document_type}'."
            )

        documents[document_type] = document

    return documents
