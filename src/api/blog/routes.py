from datetime import datetime, timezone
from http import HTTPStatus
from typing import List, Optional
from urllib.parse import urljoin

from beanie import PydanticObjectId
from fastapi import HTTPException, Response
from starlette.requests import Request

from .app import app
from .models import (BlogPost, Category, Comment, CreateUpdateBlogPost,
                     CreateUpdateCategory, CreateUpdateComment)


# Import the chat agent function - lazy import to avoid initialization issues
# import sys
# import os
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'chat'))
# from agent import chat_with_agent


# Health check endpoint (no database dependency)
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy", "message": "API is running"}


@app.get("/test-beanie")
async def test_beanie():
    """Test Beanie initialization"""
    try:
        from .app import ensure_beanie_initialized
        await ensure_beanie_initialized()
        
        from .models import BlogPost
        # Try to count documents
        count = await BlogPost.count()
        return {"status": "success", "blog_posts_count": count}
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return {"status": "error", "error": str(e), "traceback": error_detail}


# Category routes
@app.get("/categories", response_model=List[Category], response_model_by_alias=False)
async def get_categories(
    top: Optional[int] = None, skip: Optional[int] = None
) -> List[Category]:
    """
    Get all categories

    Optional arguments:
    - **top**: Number of categories to return
    - **skip**: Number of categories to skip
    """
    query = Category.all().skip(skip).limit(top)
    return await query.to_list()


@app.post("/categories", response_model=Category, response_model_by_alias=False, status_code=201)
async def create_category(body: CreateUpdateCategory, request: Request, response: Response) -> Category:
    """
    Create a new category
    """
    category = await Category(**body.dict(), createdDate=datetime.now(timezone.utc)).save()
    response.headers["Location"] = urljoin(str(request.base_url), f"categories/{category.id}")
    return category


@app.get("/categories/{category_id}", response_model=Category, response_model_by_alias=False)
async def get_category(category_id: PydanticObjectId) -> Category:
    """
    Get category by ID
    """
    category = await Category.get(document_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.put("/categories/{category_id}", response_model=Category, response_model_by_alias=False)
async def update_category(
    category_id: PydanticObjectId, body: CreateUpdateCategory
) -> Category:
    """
    Updates a category by unique identifier
    """
    category = await Category.get(document_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await category.update({"$set": body.dict(exclude_unset=True)})
    category.updatedDate = datetime.now(timezone.utc)
    return await category.save()


@app.delete("/categories/{category_id}", response_class=Response, status_code=204)
async def delete_category(category_id: PydanticObjectId) -> None:
    """
    Deletes a category by unique identifier
    """
    category = await Category.get(document_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await category.delete()


# Blog post routes
@app.get("/posts", response_model=List[BlogPost], response_model_by_alias=False)
async def get_posts(
    published: Optional[bool] = None,
    category_id: Optional[PydanticObjectId] = None,
    top: Optional[int] = None,
    skip: Optional[int] = None
) -> List[BlogPost]:
    """
    Get all blog posts

    Optional arguments:
    - **published**: Filter by published status
    - **category_id**: Filter by category
    - **top**: Number of posts to return
    - **skip**: Number of posts to skip
    """
    from .app import ensure_beanie_initialized
    await ensure_beanie_initialized()
    
    query = BlogPost.all()

    if published is not None:
        query = query.find(BlogPost.published == published)

    if category_id:
        query = query.find(BlogPost.categoryId == category_id)

    query = query.skip(skip).limit(top)
    return await query.to_list()


@app.post("/posts", response_model=BlogPost, response_model_by_alias=False, status_code=201)
async def create_post(body: CreateUpdateBlogPost, request: Request, response: Response) -> BlogPost:
    """
    Create a new blog post
    """
    post_data = body.dict()
    if body.published and not body.publishedDate:
        post_data["publishedDate"] = datetime.now(timezone.utc)

    post = await BlogPost(**post_data, createdDate=datetime.now(timezone.utc)).save()
    response.headers["Location"] = urljoin(str(request.base_url), f"posts/{post.id}")
    return post


@app.get("/posts/{post_id}", response_model=BlogPost, response_model_by_alias=False)
async def get_post(post_id: PydanticObjectId) -> BlogPost:
    """
    Get blog post by ID
    """
    post = await BlogPost.get(document_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post


@app.put("/posts/{post_id}", response_model=BlogPost, response_model_by_alias=False)
async def update_post(
    post_id: PydanticObjectId, body: CreateUpdateBlogPost
) -> BlogPost:
    """
    Updates a blog post by unique identifier
    """
    post = await BlogPost.get(document_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    update_data = body.dict(exclude_unset=True)
    if body.published and not post.publishedDate:
        update_data["publishedDate"] = datetime.now(timezone.utc)

    await post.update({"$set": update_data})
    post.updatedDate = datetime.now(timezone.utc)
    return await post.save()


@app.delete("/posts/{post_id}", response_class=Response, status_code=204)
async def delete_post(post_id: PydanticObjectId) -> None:
    """
    Deletes a blog post by unique identifier
    """
    post = await BlogPost.get(document_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    await post.delete()


# Comment routes
@app.get("/posts/{post_id}/comments", response_model=List[Comment], response_model_by_alias=False)
async def get_post_comments(
    post_id: PydanticObjectId,
    approved: Optional[bool] = None,
    top: Optional[int] = None,
    skip: Optional[int] = None
) -> List[Comment]:
    """
    Get comments for a specific blog post

    Optional arguments:
    - **approved**: Filter by approval status
    - **top**: Number of comments to return
    - **skip**: Number of comments to skip
    """
    query = Comment.find(Comment.postId == post_id)

    if approved is not None:
        query = query.find(Comment.approved == approved)

    query = query.skip(skip).limit(top)
    return await query.to_list()


@app.post("/posts/{post_id}/comments", response_model=Comment, response_model_by_alias=False, status_code=201)
async def create_comment(
    post_id: PydanticObjectId,
    body: CreateUpdateComment,
    request: Request,
    response: Response
) -> Comment:
    """
    Create a new comment for a blog post
    """
    comment = await Comment(
        postId=post_id,
        **body.dict(),
    createdDate=datetime.now(timezone.utc)
    ).save()
    response.headers["Location"] = urljoin(str(request.base_url), f"posts/{post_id}/comments/{comment.id}")
    return comment


@app.put("/posts/{post_id}/comments/{comment_id}", response_model=Comment, response_model_by_alias=False)
async def update_comment(
    post_id: PydanticObjectId,
    comment_id: PydanticObjectId,
    body: CreateUpdateComment
) -> Comment:
    """
    Updates a comment by unique identifier
    """
    comment = await Comment.find_one(
        Comment.id == comment_id,
        Comment.postId == post_id
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    await comment.update({"$set": body.dict(exclude_unset=True)})
    comment.updatedDate = datetime.now(timezone.utc)
    return await comment.save()


@app.delete("/posts/{post_id}/comments/{comment_id}", response_class=Response, status_code=204)
async def delete_comment(
    post_id: PydanticObjectId,
    comment_id: PydanticObjectId
) -> None:
    """
    Deletes a comment by unique identifier
    """
    comment = await Comment.find_one(
        Comment.id == comment_id,
        Comment.postId == post_id
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    await comment.delete()


# Chat endpoint
from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat with the AI agent with conversation history support
    """
    try:
        # Lazy import to avoid initialization issues during app startup
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'chat'))
        from agent import chat_with_agent
        
        result = await chat_with_agent(request.message, request.conversation_history, request.conversation_id)
        return ChatResponse(response=result["response"], conversation_id=result["conversation_id"])
    except Exception as e:
        import ast
        import re

        # Try to parse an embedded dict in the exception text (e.g. "Agent run failed: {'code': 'rate_limit_exceeded', 'message': '...'}")
        text = str(e)
        parsed = None
        try:
            # Find the first {...} substring and parse it as a Python literal
            m = re.search(r"\{.*\}", text)
            if m:
                parsed = ast.literal_eval(m.group(0))
        except Exception:
            parsed = None

        # If structured error indicates rate limiting, return 429 with Retry-After
        if isinstance(parsed, dict) and parsed.get('code') == 'rate_limit_exceeded':
            # Try to extract suggested seconds from message, fallback to 60
            msg_text = str(parsed.get('message', ''))
            sec_match = re.search(r"(\d+)\s*second", msg_text)
            retry_after = int(sec_match.group(1)) if sec_match else 60
            raise HTTPException(status_code=429, detail=msg_text or f"Rate limit exceeded. Try again in {retry_after} seconds.", headers={"Retry-After": str(retry_after)})

        # Fallback: simple string match for rate limit
        low = text.lower()
        if 'rate_limit_exceeded' in low or 'rate limit' in low:
            retry_after = 60
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Try again in {retry_after} seconds.", headers={"Retry-After": str(retry_after)})

        # Otherwise return generic 500 with original message
        raise HTTPException(status_code=500, detail=f"Chat error: {text}")
