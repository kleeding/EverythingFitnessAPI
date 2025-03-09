import pytest
from app import schemas


def test_get_posts_not_logged_in(client):
    res = client.get("/posts/")

    assert res.status_code == 401


def test_get_posts_none_exist(authorized_client):
    res = authorized_client.get("/posts/")

    assert res.status_code == 404


def test_get_posts(authorized_client, test_posts, test_user):
    res = authorized_client.get("/posts/")

    def validate_post(post):
        return schemas.PostOut(**post)

    post_map = map(validate_post, res.json())
    posts_list = list(post_map)

    assert len(posts_list) == 10
    assert res.status_code == 200


@pytest.mark.parametrize(
    "limit, return_length",
    [(1, 1), (3, 3), (6, 6), (10, 10), (20, 18), (50, 18)],
)
def test_get_posts_limit(authorized_client, test_posts, limit, return_length):
    res = authorized_client.get(f"/posts/?limit={limit}")

    def validate_post(post):
        return schemas.PostOut(**post)

    post_map = map(validate_post, res.json())
    posts_list = list(post_map)

    assert len(posts_list) == return_length
    assert res.status_code == 200


@pytest.mark.parametrize(
    "offset, return_length",
    [(1, 10), (3, 10), (6, 10), (10, 8), (15, 3)],
)
def test_get_posts_offset(authorized_client, test_posts, offset, return_length):
    res = authorized_client.get(f"/posts/?offset={offset}")

    def validate_post(post):
        return schemas.PostOut(**post)

    post_map = map(validate_post, res.json())
    posts_list = list(post_map)

    assert len(posts_list) == return_length
    assert res.status_code == 200


def test_get_posts_offset_no_result(authorized_client, test_posts):
    res = authorized_client.get("/posts/?offset=50")

    assert res.status_code == 404


@pytest.mark.parametrize(
    "search, return_length",
    [
        ("1st", 3),
        ("u1", 12),
        ("pub", 12),
        ("pri", 6),
    ],
)
def test_get_posts_search(authorized_client, test_posts, search, return_length):
    res = authorized_client.get(f"/posts/?search={search}&limit=24")

    def validate_post(post):
        assert search in post.get("Post")["title"]
        return schemas.PostOut(**post)

    post_map = map(validate_post, res.json())
    posts_list = list(post_map)

    assert len(posts_list) == return_length
    assert res.status_code == 200


@pytest.mark.parametrize(
    "owner_id, return_length",
    [
        (1, 12),
        (2, 6),
    ],
)
def test_get_posts_owner_id(
    authorized_client, test_user, test_posts, owner_id, return_length
):
    res = authorized_client.get(f"/posts/?owner_id={owner_id}&limit=24")

    def validate_post(post):
        assert post.get("Post")["owner_id"] == owner_id
        if owner_id != test_user["id"]:
            assert post.get("Post")["private"] == False
        return schemas.PostOut(**post)

    post_map = map(validate_post, res.json())
    posts_list = list(post_map)

    assert len(posts_list) == return_length
    assert res.status_code == 200


def test_get_post_unauthorized_no_posts(client):
    res = client.get("/posts/1")

    assert res.status_code == 401


def test_get_post_unauthorized(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401


def test_get_post_no_posts(authorized_client):
    res = authorized_client.get("/posts/1")

    assert res.status_code == 404


def test_get_post_no_post_with_give_id(authorized_client, test_posts):
    res = authorized_client.get("/posts/9999")

    assert res.status_code == 404


def test_get_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")

    post = schemas.PostOut(**res.json())

    assert res.status_code == 200
    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.Post.content == test_posts[0].content
    assert post.Post.private == test_posts[0].private
    assert post.Post.created_at == test_posts[0].created_at
    assert post.Post.owner_id == test_posts[0].owner_id
    assert post.Post.owner.username == test_posts[0].owner.username
    assert post.Post.owner.created_at == test_posts[0].owner.created_at


@pytest.mark.parametrize(
    "post_id, status_code",
    [
        (1, 200),  # test_user 1's post - public
        (7, 200),  # test_user 1's post - private
        (13, 200),  # test_user 2's post - public
        (19, 401),  # test_user 2's post - private
    ],
)
def test_get_post_private_post(authorized_client, test_posts, post_id, status_code):
    res = authorized_client.get(f"/posts/{post_id}")

    assert res.status_code == status_code


def test_create_post_unauthorized(client):
    res = client.post("/posts/", json={"title": "title", "content": "content"})

    assert res.status_code == 401


@pytest.mark.parametrize(
    "title, content, private",
    [
        ("test title1", "test content1", True),
        ("test title2", "test content2", False),
    ],
)
def test_create_post(authorized_client, test_user, title, content, private):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "private": private}
    )

    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.private == private
    assert created_post.owner_id == test_user["id"]


def test_create_post_default_private(authorized_client, test_user):

    res = authorized_client.post(
        "/posts/", json={"title": "title", "content": "content"}
    )

    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == "title"
    assert created_post.content == "content"
    assert created_post.private == True
    assert created_post.owner_id == test_user["id"]


def test_delete_post_unauthorized(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401


def test_delete_post_non_exist(authorized_client):
    res = authorized_client.delete("/posts/1")

    assert res.status_code == 404


def test_delete_post_invalid_id(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/99999")

    assert res.status_code == 404


def test_delete_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 204


def test_delete_post_other_user_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[12].id}")

    assert res.status_code == 403


"""
- invalid id
- update good
- unauthorised
- others post

"""


def test_update_post_unauthorized(client, test_posts):
    res = client.put(
        f"/posts/{test_posts[0].id}",
        json={"title": "updated title", "content": "updated content"},
    )

    assert res.status_code == 401


def test_update_post_non_exists(authorized_client, test_posts):
    res = authorized_client.put(
        "/posts/99999",
        json={"title": "updated title", "content": "updated content"},
    )

    assert res.status_code == 404


def test_update_post(authorized_client, test_posts):
    res = authorized_client.put(
        f"/posts/{test_posts[0].id}",
        json={"title": "updated title", "content": "updated content", "private": True},
    )

    updated_post = schemas.Post(**res.json())

    assert res.status_code == 200
    assert updated_post.title == "updated title"
    assert updated_post.content == "updated content"
    assert updated_post.private == True


def test_update_post_other_owner(authorized_client, test_posts):
    res = authorized_client.put(
        f"/posts/{test_posts[12].id}",
        json={"title": "updated title", "content": "updated content"},
    )

    assert res.status_code == 403
