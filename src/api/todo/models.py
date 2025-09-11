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

        # Load secrets from keyvault
        if self.AZURE_KEY_VAULT_ENDPOINT:
            credential = DefaultAzureCredential()
            keyvault_client = SecretClient(self.AZURE_KEY_VAULT_ENDPOINT, credential)
            for secret in keyvault_client.list_properties_of_secrets():
                setattr(
                    self,
                    keyvault_name_as_attr(secret.name),
                    keyvault_client.get_secret(secret.name).value,
                )

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
