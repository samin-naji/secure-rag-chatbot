import argparse

from app.core.database import SessionLocal
from app.services.retrieval import search_similar_chunks


def main():

    parser = argparse.ArgumentParser(
        description="Test semantic search with pgvector"
    )

    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Question or search text"
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results"
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:

        results = search_similar_chunks(
            db=db,
            query=args.query,
            top_k=args.top_k
        )

        if not results:
            print("No matching chunks found.")
            return

        print("\nSemantic Search Results")
        print("=" * 60)

        for index, result in enumerate(results, start=1):

            print(f"\nResult #{index}")
            print("-" * 40)

            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Document ID: {result['document_id']}")
            print(f"Filename: {result['filename']}")
            print(f"Chunk Index: {result['chunk_index']}")

            print(
                f"Similarity: "
                f"{result['similarity']:.4f}"
            )

            print("\nContent:")
            print(result["content"])

        print("\n" + "=" * 60)
        print(f"Total results: {len(results)}")

    except Exception as exc:

        print(f"Semantic search failed: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
