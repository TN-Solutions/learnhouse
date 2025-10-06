#!/usr/bin/env python3
"""
Script to reset admin password for LearnHouse
Usage: python reset_admin_password.py [new_password]
If no password is provided, a random password will be generated.
"""

import sys
import random
import string
from sqlalchemy import create_engine
from sqlmodel import Session, select
from config.config import get_learnhouse_config
from src.security.security import security_hash_password
from src.db.users import User

def generate_password(length=12):
    """Generate a random password with uppercase, lowercase and digits"""
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def reset_admin_password(new_password=None):
    """Reset password for admin@school.dev user"""

    # Get configuration
    learnhouse_config = get_learnhouse_config()

    # Create database connection
    engine = create_engine(
        learnhouse_config.database_config.sql_connection_string,
        echo=False,
        pool_pre_ping=True
    )

    # Create session
    with Session(engine) as db_session:
        try:
            # Find admin user
            statement = select(User).where(User.email == "admin@school.dev")
            admin_user = db_session.exec(statement).first()

            if not admin_user:
                print("❌ Admin user admin@school.dev not found!")
                print("Available users:")
                users = db_session.exec(select(User)).all()
                for user in users:
                    print(f"  - {user.email} ({user.username})")
                return False

            # Generate password if not provided
            if not new_password:
                new_password = generate_password(12)
                print(f"🔑 Generated new password: {new_password}")

            # Hash the password
            hashed_password = security_hash_password(new_password)

            # Update user password
            admin_user.password = hashed_password
            db_session.add(admin_user)
            db_session.commit()
            db_session.refresh(admin_user)

            print("✅ Password updated successfully!")
            print(f"📧 Email: admin@school.dev")
            print(f"🔑 Password: {new_password}")
            print("⚠️ Please change this password after logging in!")

            return True

        except Exception as e:
            print(f"❌ Error updating password: {str(e)}")
            db_session.rollback()
            return False

def main():
    """Main function"""
    print("🔧 LearnHouse Admin Password Reset Tool")
    print("=" * 50)

    # Get password from command line or generate one
    new_password = None
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
        print(f"🔑 Using provided password: {new_password}")
    else:
        print("🎲 No password provided, will generate a random one")

    # Reset password
    success = reset_admin_password(new_password)

    if success:
        print("\n🎉 Password reset completed successfully!")
        print("You can now login with the new credentials.")
    else:
        print("\n❌ Password reset failed!")
        print("Please check the error message above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()