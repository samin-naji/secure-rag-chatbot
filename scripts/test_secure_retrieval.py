import argparse

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.user import User
from app.services.retrieval import search_similar_chunks


def main():

    parser = argparse.ArgumentParser(
        description="Test secure semantic retrieval"
    )

    parser.add_argument(
        "--username",
        required=True,
        help="Username of the user performing the search"
    )

    parser.add_argument(
        "--query",
        required=True,
        help="Semantic search query"
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:

        # Step 1: Load user
        user = db.scalar(
            select(User).where(
                User.username == args.username
            )
        )

        if user is None or not user.is_active:
            print("User not found or inactive.")
            return

        print("\nSecure Retrieval Test")
        print("=" * 60)

        print(f"Username: {user.username}")
        print(f"Role: {user.role}")
        print(f"Department: {user.department}")

        # Step 2: Perform secure search
        results = search_similar_chunks(
            db=db,
            user=user,
            query=args.query,
            top_k=args.top_k
        )

        # Step 3: Display authorized results
        print("\nSearch Results")
        print("-" * 60)

        if not results:
            print("No accessible matching chunks found.")

        for index, result in enumerate(results, start=1):

            print(f"\nResult #{index}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Document ID: {result['document_id']}")
            print(f"Filename: {result['filename']}")
            print(f"Similarity: {result['similarity']:.4f}")

            print("\nContent:")
            print(result["content"])

        print("\n" + "=" * 60)
        print(f"Total accessible results: {len(results)}")

        # Step 4: Verify returned document permissions
        returned_document_ids = {
            result["document_id"]
            for result in results
        }

        if user.role == "admin":
            print("Access rule: Admin - all documents allowed.")

        else:
            print(
                "Access rule: Explicit read permission required."
            )

        print(
            "Returned document IDs:",
            sorted(returned_document_ids)
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
