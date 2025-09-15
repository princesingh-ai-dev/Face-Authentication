import sys
from authenticator import Authenticator


def main() -> int:
    print("Face Enrollment")
    print("----------------")
    user_id = input("Enter a unique user ID to enroll: ").strip()
    if not user_id:
        print("User ID cannot be empty.")
        return 1

    authenticator = Authenticator()
    try:
        success = authenticator.enroll_user(user_id=user_id)
        if success:
            print(f"Enrollment complete for {user_id}.")
            return 0
        else:
            print("Enrollment failed. Try again with better lighting and a single face in frame.")
            return 2
    except Exception as exc:
        print(f"Error during enrollment: {exc}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
