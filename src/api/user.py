import time

# user_profiles maps username to a profile dict
user_profiles = {}  # Example: {"alice": {"holdings": 10, "created_at": ...}}

def get_or_create_profile(username: str):
    if username not in user_profiles:
        user_profiles[username] = {
            "holdings": 0,
            "created_at": time.time()
        }
    return user_profiles[username]