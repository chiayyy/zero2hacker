import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from app.core.config import settings
import json


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        # For development, use a service account key file
        # In production, use environment variables or IAM roles
        try:
            if settings.FIREBASE_PRIVATE_KEY:
                # Use environment variables
                cred_dict = {
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                    "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                    "client_email": settings.FIREBASE_CLIENT_EMAIL,
                    "client_id": settings.FIREBASE_CLIENT_ID,
                    "auth_uri": settings.FIREBASE_AUTH_URI,
                    "token_uri": settings.FIREBASE_TOKEN_URI,
                }
                cred = credentials.Certificate(cred_dict)
            else:
                # Use default credentials (for development)
                cred = credentials.ApplicationDefault()

            firebase_admin.initialize_app(cred, {
                'projectId': settings.FIREBASE_PROJECT_ID,
                'storageBucket': f'{settings.FIREBASE_PROJECT_ID}.appspot.com'
            })
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            # Initialize with minimal config for development
            firebase_admin.initialize_app()


def get_firestore_client():
    """Get Firestore client"""
    return firestore.client()


def get_auth_client():
    """Get Firebase Auth client"""
    return auth


def get_storage_client():
    """Get Firebase Storage client"""
    return storage.bucket()