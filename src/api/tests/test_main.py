def test_blog_post_and_comments_crud(app_client):
    # Ensure a clean slate: delete any pre-existing posts (from previous runs)
    existing = app_client.get("/posts")
    assert existing.status_code == 200
    for p in existing.json():
        app_client.delete(f"/posts/{p['id']}")

    # Create two blog posts
    first = app_client.post(
        "/posts",
        json={
            "title": "First Post",
            "content": "Content of first post",
            "excerpt": "Excerpt 1",
            "author": "Alice",
            "slug": "first-post",
            "published": True
        },
    )
    assert first.status_code == 201, first.text
    assert first.headers["Location"].startswith("http://testserver/posts/")

    second = app_client.post(
        "/posts",
        json={
            "title": "Second Post",
            "content": "Content of second post",
            "excerpt": "Excerpt 2",
            "author": "Bob",
            "slug": "second-post",
            "published": False
        },
    )
    assert second.status_code == 201, second.text

    # List posts
    list_resp = app_client.get("/posts")
    assert list_resp.status_code == 200
    posts = list_resp.json()
    assert len(posts) == 2
    # Order not guaranteed; verify by titles set
    titles = {p["title"] for p in posts}
    assert {"First Post", "Second Post"} == titles
    first_id = next(p["id"] for p in posts if p["title"] == "First Post")
    second_id = next(p["id"] for p in posts if p["title"] == "Second Post")

    # Get single post
    get_first = app_client.get(f"/posts/{first_id}")
    assert get_first.status_code == 200
    post_body = get_first.json()
    assert post_body["title"] == "First Post"
    assert post_body["author"] == "Alice"
    assert post_body["createdDate"] is not None

    # Bad ID (24 hex chars but unlikely to exist)
    not_found = app_client.get("/posts/61958439e0dbd854f5ab9000")
    assert not_found.status_code == 404

    # Update second post -> publish and change title
    upd = app_client.put(
        f"/posts/{second_id}",
        json={
            "title": "Second Post Updated",
            "content": "Content of second post",
            "excerpt": "Excerpt 2",
            "author": "Bob",
            "slug": "second-post",
            "published": True
        },
    )
    assert upd.status_code == 200, upd.text
    upd_json = upd.json()
    assert upd_json["title"] == "Second Post Updated"
    assert upd_json["updatedDate"] is not None
    assert upd_json["published"] is True

    # Create a comment on first post
    comment_resp = app_client.post(
        f"/posts/{first_id}/comments",
        json={
            "author": "Charlie",
            "content": "Great post!",
            "approved": False
        },
    )
    assert comment_resp.status_code == 201, comment_resp.text
    assert comment_resp.headers["Location"].startswith(f"http://testserver/posts/{first_id}/comments/")
    comment_id = comment_resp.json()["id"]

    # List comments
    comments_list = app_client.get(f"/posts/{first_id}/comments")
    assert comments_list.status_code == 200
    comments = comments_list.json()
    assert len(comments) == 1
    assert comments[0]["author"] == "Charlie"
    assert comments[0]["content"] == "Great post!"

    # Update comment (approve)
    upd_comment = app_client.put(
        f"/posts/{first_id}/comments/{comment_id}",
        json={
            "author": "Charlie",
            "content": "Great post!",
            "approved": True
        },
    )
    assert upd_comment.status_code == 200, upd_comment.text
    assert upd_comment.json()["approved"] is True

    # Delete comment
    del_comment = app_client.delete(f"/posts/{first_id}/comments/{comment_id}")
    assert del_comment.status_code == 204
    # Verify deleted
    comments_after = app_client.get(f"/posts/{first_id}/comments")
    assert comments_after.status_code == 200
    assert comments_after.json() == []

    # Delete a post
    del_post = app_client.delete(f"/posts/{second_id}")
    assert del_post.status_code == 204
    check_deleted = app_client.get(f"/posts/{second_id}")
    assert check_deleted.status_code == 404

    # Remaining posts list should be 1
    remaining = app_client.get("/posts")
    assert remaining.status_code == 200
    assert len(remaining.json()) == 1
