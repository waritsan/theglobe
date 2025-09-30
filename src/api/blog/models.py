from datetime import datetime
from enum import Enum
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, BaseSettings

def keyvault_name_as_attr(name: str) -> str:
    return name.replace("-", "_").upper()


class Settings(BaseSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Try to load from Key Vault first if endpoint is available, but fall back to env vars
        if self.AZURE_KEY_VAULT_ENDPOINT:
            try:
                credential = DefaultAzureCredential()
                keyvault_client = SecretClient(self.AZURE_KEY_VAULT_ENDPOINT, credential)
                secrets_loaded = 0
                for secret in keyvault_client.list_properties_of_secrets():
                    if secret.name:
                        value = keyvault_client.get_secret(secret.name).value
                        if value:  # Only set if value is not empty
                            setattr(self, keyvault_name_as_attr(secret.name), value)
                            secrets_loaded += 1
                if secrets_loaded > 0:
                    print(f"Successfully loaded {secrets_loaded} secrets from Key Vault")
                else:
                    print("Key Vault accessible but no secrets found, using environment variables")
            except Exception as e:
                print(f"Key Vault access failed: {e}, using environment variables")
        else:
            print("Key Vault endpoint not configured, using environment variables")

    AZURE_COSMOS_CONNECTION_STRING: str = ""
    AZURE_COSMOS_DATABASE_NAME: str = "Blog"
    AZURE_KEY_VAULT_ENDPOINT: Optional[str] = None
    APPLICATIONINSIGHTS_CONNECTION_STRING: Optional[str] = None
    APPLICATIONINSIGHTS_ROLENAME: Optional[str] = "API"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Category(Document):
    name: str
    description: Optional[str] = None
    slug: str  # URL-friendly identifier
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None


class CreateUpdateCategory(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str


class BlogPost(Document):
    title: str
    content: str
    excerpt: Optional[str] = None
    author: str
    categoryId: Optional[PydanticObjectId] = None
    tags: Optional[list[str]] = []
    slug: str  # URL-friendly identifier
    published: bool = False
    publishedDate: Optional[datetime] = None
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None
    imageUrl: Optional[str] = None  # Featured image URL


class CreateUpdateBlogPost(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    author: str
    categoryId: Optional[PydanticObjectId] = None
    tags: Optional[list[str]] = []
    slug: str
    published: bool = False
    publishedDate: Optional[datetime] = None
    imageUrl: Optional[str] = None


class Comment(Document):
    postId: PydanticObjectId
    author: str
    email: Optional[str] = None
    content: str
    approved: bool = False
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None


class CreateUpdateComment(BaseModel):
    author: str
    email: Optional[str] = None
    content: str
    approved: bool = False


__beanie_models__ = [Category, BlogPost, Comment]
