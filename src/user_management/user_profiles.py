"""
Simple user profile management for the Smart Mirror
"""

# Sample user profiles with their locations
USER_PROFILES = {
    "user1": {
        "name": "John",
        "location": {
            "name": "Chandler, AZ",
            "lat": 33.3062,
            "lon": -111.8413
        }
    },
    "user2": {
        "name": "Jane",
        "location": {
            "name": "Phoenix, AZ",
            "lat": 33.4484,
            "lon": -112.0740
        }
    }
}

def get_user_by_id(user_id):
    """Get a user profile by ID"""
    return USER_PROFILES.get(user_id)

def get_default_user():
    """Get the default user (no user recognized)"""
    return {
        "name": "Guest",
        "location": "default"  # This will use Brasov, Romania
    }

def get_all_users():
    """Get all user profiles"""
    return USER_PROFILES