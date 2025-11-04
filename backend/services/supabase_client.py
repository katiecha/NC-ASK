"""
Supabase client configuration and utilities
"""
import logging

from supabase import Client, create_client

from services.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Singleton Supabase client wrapper"""

    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            try:
                # Validate credentials before attempting connection
                if not settings.SUPABASE_URL or settings.SUPABASE_URL == "https://your-project.supabase.co":
                    msg = "SUPABASE_URL not configured. Please set SUPABASE_URL environment variable."
                    logger.error(msg)
                    raise ValueError(msg)
                if not settings.SUPABASE_ANON_KEY or settings.SUPABASE_ANON_KEY == "your_anon_key_here":
                    msg = "SUPABASE_ANON_KEY not configured. Please set SUPABASE_ANON_KEY environment variable."
                    logger.error(msg)
                    raise ValueError(msg)

                cls._instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
        return cls._instance

    @classmethod
    def get_admin_client(cls) -> Client:
        """Get Supabase client with service role key for admin operations"""
        try:
            # Validate credentials before attempting connection
            if not settings.SUPABASE_URL or settings.SUPABASE_URL == "https://your-project.supabase.co":
                msg = "SUPABASE_URL not configured. Please set SUPABASE_URL environment variable."
                logger.error(msg)
                raise ValueError(msg)
            if not settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_SERVICE_ROLE_KEY == "your_service_role_key_here":
                msg = "SUPABASE_SERVICE_ROLE_KEY not configured. Please set SUPABASE_SERVICE_ROLE_KEY environment variable."
                logger.error(msg)
                raise ValueError(msg)

            admin_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            logger.info("Supabase admin client initialized")
            return admin_client
        except Exception as e:
            logger.error(f"Failed to initialize Supabase admin client: {e}")
            raise


# Convenience function
def get_supabase() -> Client:
    """Get Supabase client instance"""
    return SupabaseClient.get_client()
