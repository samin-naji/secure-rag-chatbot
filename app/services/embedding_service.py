from sentence_transformers import SentenceTransformer


_model = None


def get_embedding_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    return _model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate normalized embeddings for multiple text chunks.
    """

    if not isinstance(texts, list) or not texts:
        raise ValueError("Texts must be a non-empty list.")

    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("All texts must be non-empty strings.")

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    results = embeddings.tolist()

    if len(results) != len(texts):
        raise ValueError("Embedding count does not match text count.")

    for embedding in results:
        if len(embedding) != 384:
            raise ValueError(
                f"Expected 384 dimensions, got {len(embedding)}"
            )

    return results


def generate_embedding(text: str) -> list[float]:
    """
    Generate embedding for a single text.
    """

    return generate_embeddings([text])[0]
