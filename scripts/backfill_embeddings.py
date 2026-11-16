import argparse

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


def backfill_embeddings(batch_size: int = 20):
    """
    Generate and save embeddings for chunks
    that currently have NULL embeddings.
    """

    db = SessionLocal()

    total_processed = 0

    try:
        while True:

            # Step 1: Find chunks without embeddings
            chunks = db.scalars(
                select(DocumentChunk)
                .where(DocumentChunk.embedding.is_(None))
                .order_by(DocumentChunk.id)
                .limit(batch_size)
            ).all()

            if not chunks:
                break

            print(
                f"Processing batch of {len(chunks)} chunks..."
            )

            # Step 2: Generate and assign embeddings
            for chunk in chunks:

                embedding = generate_embedding(chunk.content)

                if len(embedding) != 384:
                    raise ValueError(
                        f"Invalid embedding dimension "
                        f"for chunk ID {chunk.id}"
                    )

                chunk.embedding = embedding

                print(
                    f"Embedding generated for chunk ID: {chunk.id}"
                )

            # Step 3: Save current batch
            db.commit()

            total_processed += len(chunks)

            print(
                f"Batch saved successfully. "
                f"Total processed: {total_processed}"
            )

        print("\nBackfill completed successfully.")
        print(f"Total chunks processed: {total_processed}")

    except Exception as exc:

        db.rollback()

        print("\nBackfill failed.")
        print(f"Error: {exc}")

        raise

    finally:
        db.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Backfill missing document embeddings"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Number of chunks processed per batch"
    )

    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("--batch-size must be greater than zero")

    backfill_embeddings(
        batch_size=args.batch_size
    )
